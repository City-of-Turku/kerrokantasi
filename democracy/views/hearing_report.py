import io

import xlsxwriter
import json
from django.conf import settings
from django.http import HttpResponse

from xlsxwriter.utility import xl_rowcol_to_cell
from democracy.models import SectionComment

from .section_comment import SectionCommentSerializer


class HearingReport(object):

    def __init__(self, json, context=None):
        self.json = json
        self.buffer = io.BytesIO()
        self.xlsdoc = xlsxwriter.Workbook(self.buffer, {'in_memory': True})
        self.hearing_worksheet = self.xlsdoc.add_worksheet('Hearing')
        self.hearing_worksheet.set_landscape()
        self.hearing_worksheet_active_row = 0
        self.comments_worksheet = self.xlsdoc.add_worksheet('Comments')
        self.comments_worksheet.set_landscape()
        self.comments_worksheet_active_row = 0
        self.polls_worksheet = self.xlsdoc.add_worksheet('Polls')
        self.polls_worksheet.set_landscape()
        self.polls_worksheet_active_row = 0
        self.format_bold = self.xlsdoc.add_format({'bold': True})
        self.format_percent = self.xlsdoc.add_format({'num_format': '0 %'})
        self.context = context

    def add_hearing_row(self, label, content):
        row = self.hearing_worksheet_active_row
        self.hearing_worksheet.write(row, 0, label, self.format_bold)
        self.hearing_worksheet.write(row, 1, content)
        self.hearing_worksheet_active_row += 1

    def _get_default_translation(self, field):
        lang = settings.LANGUAGE_CODE
        if field.get(lang):
            return field.get(lang)
        for lang, value in field.items():
            if value:
                return value

    def generate_hearing_worksheet(self):
        self.hearing_worksheet.set_column('A:A', 20)
        self.hearing_worksheet.set_column('B:B', 200)

        # add header to hearing worksheet
        self.hearing_worksheet.set_header(self._get_default_translation(self.json['title']))

        for lang, title in self.json['title'].items():
            self.add_hearing_row('Title (%s)' % lang, title)
        self.add_hearing_row('Created', self.json['created_at'])
        self.add_hearing_row('Close', self.json['close_at'])
        # self.add_hearing_row('Author', self.json['created_by'])
        for lang, abstract in self.json['abstract'].items():
            self.add_hearing_row('Abstract (%s)' % lang, abstract)
        for lang, borough in self.json['borough'].items():
            self.add_hearing_row('Borough (%s)' % lang, borough)
        self.add_hearing_row('Labels', str('%s' % ', '.join([self._get_default_translation(label['label']) for label in
                                                            self.json['labels']])))
        self.add_hearing_row('Comments', str(self.json['n_comments']))
        self.add_hearing_row('Sections', str(len(self.json['sections'])))

    def add_comment_row(self, commented_section, comment):
        row = self.comments_worksheet_active_row
        # add commented section
        self.comments_worksheet.write(row, 0, commented_section)
        # add author
        self.comments_worksheet.write(row, 1, comment['author_name'])
        # add creation date
        self.comments_worksheet.write(row, 2, comment['created_at'])
        # add votes
        self.comments_worksheet.write(row, 3, comment['n_votes'])
        # add label
        self.comments_worksheet.write(row, 4, self._get_default_translation(comment['label'].get('label')
                                                                            if comment['label'] else {}))
        # add content
        self.comments_worksheet.write(row, 5, comment['content'])
        # add geojson
        self.comments_worksheet.write(row, 6, json.dumps(comment['geojson']))
        self.comments_worksheet.write(row, 7, ','.join(
            image['url'] for image in comment['images']))
        self.comments_worksheet_active_row += 1

    def generate_comments_worksheet(self):
        self.comments_worksheet.set_column('A:A', 25)
        self.comments_worksheet.set_column('B:B', 20)
        self.comments_worksheet.set_column('C:C', 20)
        self.comments_worksheet.set_column('D:D', 5)
        self.comments_worksheet.set_column('E:E', 20)
        self.comments_worksheet.set_column('F:F', 200)
        self.comments_worksheet.set_column('G:G', 100)
        self.comments_worksheet.set_column('H:H', 100)

        self.comments_worksheet.set_header('Comments of %s' % self._get_default_translation(self.json['title']))

        self.comments_worksheet.write(0, 0, 'Section', self.format_bold)
        self.comments_worksheet.write(0, 1, 'Author', self.format_bold)
        self.comments_worksheet.write(0, 2, 'Created', self.format_bold)
        self.comments_worksheet.write(0, 3, 'Votes', self.format_bold)
        self.comments_worksheet.write(0, 4, 'Label', self.format_bold)
        self.comments_worksheet.write(0, 5, 'Content', self.format_bold)
        self.comments_worksheet.write(0, 6, 'Geojson', self.format_bold)
        self.comments_worksheet.write(0, 7, 'Images', self.format_bold)

        self.comments_worksheet_active_row = 1

        comments_count = 0

        sections = [s for s in self.json['sections']]
        for s in sections:
            comments = [SectionCommentSerializer(c, context=self.context).data
                        for c in SectionComment.objects.filter(section=s['id'])]
            for comment in comments:
                self.add_comment_row('%s: %s' % (s['type_name_singular'],
                                                 self._get_default_translation(s['title'])), comment)
                comments_count += 1

        self.add_hearing_row('All comments', str(comments_count))

    
    def generate_polls_worksheet(self):
        '''
        Poll question | Poll type | Total votes | How many people answered the question
        "question?"   | "type"    | num         | num
        Options       | Votes     | Votes % 
        "1) option"   | 1         | 10%    
        "2) option"   | 9         | 90%    
        -- empty rows after each question --
        '''
        self.polls_worksheet.set_header('Polls of %s' % self._get_default_translation(self.json['title']))
        self.polls_worksheet_active_row = 0

        self.polls_worksheet.set_column('A:A', 50)
        self.polls_worksheet.set_column('B:B', 13)
        self.polls_worksheet.set_column('C:C', 10)
        self.polls_worksheet.set_column('D:D', 35)

        # find sections with questions
        sections = self.json['sections']
        questions = []
        for section in sections:
            questions.extend(section['questions'])

        # add question data for each question
        for question in questions:
            self.add_poll_question_rows(question)
            # add space between questions
            self.polls_worksheet_active_row += 2


    def add_poll_question_rows(self, question):
        '''
        Poll question | Poll type | Total votes | how many people answered the question
        "question?"   | "type"    | num         | num
        '''
        row = self.polls_worksheet_active_row
        chart_location = (row, 5) # set chart to start on the same row as headers
        # headers
        self.polls_worksheet.write(row, 0, 'Poll question', self.format_bold)
        self.polls_worksheet.write(row, 1, 'Poll type', self.format_bold)
        self.polls_worksheet.write(row, 2, 'Total votes', self.format_bold)
        self.polls_worksheet.write(row, 3, 'How many people answered the question', self.format_bold)
        self.polls_worksheet_active_row += 1

        # options total vote count
        options = question['options']
        total_options_answers = 0
        for option in options:
            total_options_answers += option['n_answers']

        # values under headers
        row = self.polls_worksheet_active_row
        question_text = self._get_default_translation(question['text'])

        self.polls_worksheet.write(row, 0, question_text)
        self.polls_worksheet.write(row, 1, question['type'])
        self.polls_worksheet.write(row, 2, total_options_answers)
        self.polls_worksheet.write(row, 3, question['n_answers'])
        # store n_answers cell location for option answer % calculation
        total_answers_cell = xl_rowcol_to_cell(row, 2)
        self.polls_worksheet_active_row += 1

        # add option rows, store option cell info
        option_cells = self.add_poll_question_option_rows(options, total_answers_cell)

        # add space after options to make room for chart (2 rows per option)
        empty_rows_after_options = len(options) * 2
        self.polls_worksheet_active_row += empty_rows_after_options
        # add chart
        self.add_poll_question_chart(question_text, option_cells, chart_location, empty_rows_after_options)

    
    def add_poll_question_option_rows(self, options, total_answers_cell):
        '''
        Options     | Votes | Votes % 
        "1) option" | 1     | 10 %    
        '''
        row = self.polls_worksheet_active_row
        # headers
        self.polls_worksheet.write(row, 0, 'Options', self.format_bold)
        self.polls_worksheet.write(row, 1, 'Votes', self.format_bold)
        self.polls_worksheet.write(row, 2, 'Votes %', self.format_bold)
        self.polls_worksheet_active_row += 1

        # store category and value start locations for later calculations
        categories_start = (self.polls_worksheet_active_row, 0)
        values_start = (self.polls_worksheet_active_row, 2)
        # values under headers
        for index, option in enumerate(options, start=1):
            row = self.polls_worksheet_active_row
            self.polls_worksheet.write(row, 0, f"{index}) {self._get_default_translation(option['text'])}")
            self.polls_worksheet.write(row, 1, option['n_answers'])
            self.polls_worksheet.write(row, 2, f"={xl_rowcol_to_cell(row, 1)}/{total_answers_cell}", self.format_percent)
            self.polls_worksheet_active_row += 1

        # store category and value end locations for later calculations
        categories_end = (self.polls_worksheet_active_row-1, 0) # -1 row to not include empty row
        values_end = (self.polls_worksheet_active_row-1, 2) # -1 row to not include empty row

        # return dict containing option cell info
        return {
            'categories_start': categories_start,
            'values_start': values_start,
            'categories_end': categories_end,
            'values_end': values_end,
            'option_count': len(options)
            }
    
    def add_poll_question_chart(self, question_text, option_cells, chart_location, empty_rows_after_options = 0):        
        chart = self.xlsdoc.add_chart({'type': 'bar'})
        # Configure the series.
        # [sheetname, first_row, first_col, last_row, last_col]
        chart.add_series({
            'categories': ['Polls', option_cells['categories_start'][0], option_cells['categories_start'][1],
                option_cells['categories_end'][0], option_cells['categories_end'][1]], 
            'values':     ['Polls', option_cells['values_start'][0], option_cells['values_start'][1],
                option_cells['values_end'][0], option_cells['values_end'][1]],
        })

        # Add a chart title and remove series title
        chart.set_title ({
            'name': question_text,
            'name_font': {'name': 'Calibri', 'size': 14, 'bold': False}
        }) # poll question
        chart.set_legend({'none': True}) # removes "series 1"
        
        # chart and axis styles
        #chart.set_style(1)
        chart.set_x_axis({
            'max': 1, # percent scale to always be up to 100%
            'num_font': {'name': 'Calibri', 'size': 9},
        })
        chart.set_y_axis({
            'num_font': {'name': 'Calibri', 'size': 9},
        })

        # calculate chart height
        # standard row pixel height is 20px
        # height = (header rows (3) + option rows + empty rows) * row height
        option_count = option_cells['option_count']
        chart_height = (3 + option_count + empty_rows_after_options) * 20
        chart.set_size({'width': 480, 'height': chart_height})

        # Insert the chart into the worksheet.
        self.polls_worksheet.insert_chart(chart_location[0], chart_location[1], chart)


    def get_xlsx(self):
        self.generate_hearing_worksheet()
        self.generate_comments_worksheet()
        self.generate_polls_worksheet()
        self.xlsdoc.close()

        return self.buffer.getvalue()

    def get_response(self):
        response = HttpResponse(
            self.get_xlsx(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename={filename}.xlsx'.format(
            filename=self._get_default_translation(self.json['title']))
        return response
