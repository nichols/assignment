
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from sheets import sheets
import assignment


def main():
  spreadsheet_id = '1WydOez3OoBKLvxsdUaZQ8s9d5xBK7BY9dzBIyxJXzgk'
  sheet_range = 'A1:H10'
  table = sheets.get_data_for_range(spreadsheet_id, sheet_range)

  assignment.assign(table)

if __name__ == '__main__':
  main()
