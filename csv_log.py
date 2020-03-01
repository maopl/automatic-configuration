import csv


class csv_record():

    def __init__(self, csv_filename, header):
        self.csv_filename = csv_filename
        self.buff = []
        self.line_num = 0
        self.csv_header = header
        self.buff_count = 0

        with open(self.csv_filename, 'a', encoding='utf-8', newline='') as csv_file:
            temp_header = []
            for i in self.csv_header:
                temp_header.append(i[2:])
            b_csv = csv.writer(csv_file)
            b_csv.writerow(temp_header)


    def csv_write(self, line):
        if self.buff_count < 100:
            self.buff.append(line)
            self.buff_count+=1
        else:
            with open(self.csv_filename, 'a', encoding='utf-8', newline='') as csv_file:
                b_csv = csv.writer(csv_file)
                for l in self.buff:
                    b_csv.writerow(l)
                b_csv.writerow(line)

            self.buff_count = 0

    def csv_flush(self):
        with open(self.csv_filename, 'a', encoding='utf-8', newline='') as csv_file:
            b_csv = csv.writer(csv_file)
            for l in self.buff:
                b_csv.writerow(l)





if __name__ == '__main__':
    pass
    # m_csv = csv_result('m_result.csv', [1,2,3])