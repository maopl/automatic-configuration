import os
import subprocess
import re
import  random
import csv_log
import utility
import  numpy as np
import copy
from itertools import product


file_name_list = ["akiyo_cif.y4m", "bowing_cif.y4m", "bridge_far_cif.y4m"]

switch_fmt_list = ["flv", "264", "mp4", "mkv"]



x264_arg_lst= ['--b-adapt', '--keyint', '--min-keyint', '--no-scenecut',
    '--scenecut', '--intra-refresh', '--bframes', '--b-bias', '--b-pyramid', '--open-gop',
    '--no-cabac', '--ref', '--no-deblock', '--deblock', '--slices', '--slices-max', '--slice-max-size',
    '--slice-max-mbs', '--slice-min-mbs', '--tff', '--bff', '--constrained-intra', '--pulldown', '--fake-interlaced',
    '--frame-packing', '--qp', '--bitrate', '--crf', '--rc-lookahead', '--crf-max', '--qpmin', '--qpmax', '--qpstep', '--ratetol', '--ipratio', '--pbratio',
    '--chroma-qp-offset', '--aq-mode', '--aq-strength', '--pass', '--stats', '--no-mbtree', '--qcomp',
    '--cplxblur', '--qblur', '--zones', '--no-asm','--threads',  '--seek',
    '--partitions', '--direct', '--no-weightb', '--weightp', '--me',
    '--merange', '--mvrange', '--subme', '--psy-rd', '--no-psy', '--no-mixed-refs', '--no-chroma-me',
    '--no-8x8dct', '--trellis', '--no-fast-pskip', '--no-dct-decimate', '--nr', '--deadzone-inter', '--deadzone-intra', '--cqm']


x264_arg_dic = {
         '--keyint':['range_integer', '1', '500'],'--min-keyint': ['range_integer', '1', '500'], '--scenecut': ['range_integer', '1', '300'],
         '--bframes': ['range_integer', '1', '300'], '--b-adapt': ['0','1','2'], '--b-bias': ['range_integer', '-100', '100'],
         '--b-pyramid': ['none', 'strict', 'normal'], '--ref': ['range_integer', '1', '20'], '--deblock': ['alpha:beita'],
         '--slices': ['range_integer', '0', '8'], '--slices-max': ['range_integer', '0', '8'],
         '--slice-max-size': ['range_integer', '0', '8'], '--slice-max-mbs': ['range_integer', '0', '8'],
         '--slice-min-mbs': ['range_integer', '0', '8'], '--pulldown': ['none', '22', '32', '64', 'double', 'triple', 'euro'],
         '--frame-packing': ['0','1','2','3','4','5','6','7'], '--qp': ['range_integer', '0', '81'],
         '--bitrate': ['range_integer', '1', '2000'], '--crf': ['range_float', '-12.0', '51.0'],
         '--rc-lookahead': ['range_integer', '1', '250'],'--crf-max': ['range_float', '30.0', '100.0'], '--qpmin': ['range_integer', '1', '30'],
         '--qpmax': ['range_integer', '30', '80'], '--qpstep': ['range_integer', '1', '10'],
         '--ratetol': ['range_float', '0.1', '100.0'], '--ipratio': ['range_float', '0', '5'],
         '--pbratio': ['range_float', '0', '5'], '--chroma-qp-offset': ['range_integer', '-10', '10'], '--aq-mode': ['0', '1', '2', '3'],
         '--aq-strength': ['range_float', '0', '25'], '--pass': ['1', '2', '3'],
         '--stats': ["x264_2pass.log"], '--qcomp': ['range_float', '0', '1'], '--cplxblur': ['range_float', '1', '40'],
         '--qblur': ['range_float', '-1', '2'], '--zones': ['zone'], '--threads': ['range_integer', '0', '300'],
         '--seek': ['range_integer', '0', '1000'],
         '--partitions': ['p8x8', 'p4x4', 'b8x8', 'i8x8', 'i4x4', 'none', 'all'], '--direct': ['none', 'spatial', 'temporal', 'auto'],
         '--weightp': ['0', '1', '2'], '--me': ['dia', 'hex', 'umh', 'esa', 'tesa'], '--merange': ['range_integer', '1', '64'],
         '--mvrange': ['range_integer', '1', '512'], '--subme': ['range_integer', '0', '11'],
         '--trellis': ['0', '1', '2'], '--nr': ['range_integer', '100', '1000'], '--psy-rd': ['float:float'], '--deadzone-inter': ['range_integer', '0', '32'],
         '--deadzone-intra': ['range_integer', '0', '32'], '--cqm': ['flat', 'jvt']}




special_input_arg = ['range_integer', 'range_float', 'alpha:beita', 'zone', 'float:float']


class X264_test:

    #静态变量用来计数
    access_count = 0

    def __init__(self, filename, switch_fmt, arg_list, log_obj):
        self.filename = filename
        self.width = 0
        self.height = 0
        self.pix_fmt = ""
        self.frames = 0
        self.PSNR = 0
        self.SSIM = 0
        self.error_flag = 0
        self.log_obj = log_obj

        if self.check_arg_valid(arg_list):
            self.arg_list = arg_list
            self.raw_arg = copy.deepcopy(arg_list)
        else:
            raise AssertionError

        if switch_fmt in switch_fmt_list:
            self.switch_fmt = switch_fmt
        else:
            raise AssertionError

        self.dst_filename = self.get_dst_filename()
        self.arg_list.insert(0, "../x264")
        self.arg_list.append('--psnr')
        self.arg_list.append('--ssim')
        self.arg_list.append("-o")
        self.arg_list.append(self.dst_filename)
        self.arg_list.append(self.filename)
        self.switch_info = subprocess.Popen(self.arg_list, stderr=subprocess.PIPE)
        self.set_count()


    @staticmethod
    def set_count():
        X264_test.access_count += 1

    @staticmethod
    def get_count():
        return X264_test.access_count

    @staticmethod
    def x264_err_record(err_line):
        with open('x264_err.log', 'a') as err_f:
            err_f.write(err_line)

    def get_dst_filename(self):
        temp_index = self.filename.find('.')
        dst_filename_temp = self.filename[:temp_index] + f'{self.access_count}' + '.' + self.switch_fmt
        return dst_filename_temp

    def check_arg_valid(self, arg):
        if ('--bitrate' in arg):
            b_ind = arg.index('--bitrate')
            if (arg[b_ind+1] == '0'):
                arg[b_ind + 1] = str(random.randint(1, 50))

        return True


    def get_Information(self):
        output = self.switch_info.stderr.readlines()
        error_pattern = r'x264 \[error\]:'
        SSIM_pattern = r'SSIM Mean'
        ssim_value = r'Y:(\d+\.*\d*)'
        PSNR_pattern = r'PSNR Mean'
        psnr_value = r'Avg:(\d+\.*\d*)'
        frames_num = r'encoded (\d+) frames'
        y4m_info = r'y4m \[info\]'
        width_height = r'(\d+)x(\d+)'
        for line in output:
            line = line.decode('utf-8')
            match_error = re.search(error_pattern, line)
            match_ssim = re.search(SSIM_pattern, line)
            match_psnr = re.search(PSNR_pattern, line)
            match_frame = re.search(frames_num, line)
            match_y4m = re.search(y4m_info, line)
            if match_error is not None:
                X264_test.x264_err_record(line)
                X264_test.x264_err_record(f'the err argumen is {self.raw_arg}')
                raise ValueError
            if match_ssim is not None:
                self.SSIM = float(re.search(ssim_value, line).group(1))
            if match_psnr is not None:
                self.PSNR = float(re.search(psnr_value, line).group(1))
            if match_frame is not None:
                self.frames = int(re.search(frames_num, line).group(1))
            if match_y4m is not None:
                match_y4m_info = re.search(width_height, line)
                self.width = int(match_y4m_info.group(1))
                self.height = int(match_y4m_info.group(2))


    def write_log(self):
        header_length = len(self.log_obj.csv_header)
        length = len(self.raw_arg)
        num = 0
        index = 0
        line = []
        for i in range(header_length):
            line.append(0)
        while num < length:
            temp_arg = self.raw_arg[num]
            if temp_arg in self.log_obj.csv_header:
                index = self.log_obj.csv_header.index(temp_arg)

            if temp_arg in x264_arg_dic:
                num+=1
                if x264_arg_dic[temp_arg][0] == 'range_float':
                    value = float(self.raw_arg[num])
                elif x264_arg_dic[temp_arg][0] == 'range_integer':
                    value = int(self.raw_arg[num])
                else:
                    value = self.raw_arg[num]
            else:
                value = 1
            line[index] = value
            num+=1

        line.append(self.PSNR)
        line.append(self.SSIM)
        self.log_obj.csv_write(line)

    def __call__(self, *args, **kwargs):
        try:
            self.get_Information()
        except ValueError:
            raise
        self.print_x264_info()
        self.write_log()


    def print_x264_info(self):
        print(f'count:{X264_test.access_count}, frames:{self.frames}, width:{self.width}, height:{self.height}, PSNR:{self.PSNR}, SSIM:{self.SSIM}')
        print(f'arg_Lst:{self.arg_list}')




def X264_arg_dic_process():
    new_arg_dic = {}
    for i in x264_arg_lst:
        if i in x264_arg_dic:
            # print(f'arg_num{i}, arg_type:{x264_arg_dic[i][0]}')
            if (x264_arg_dic[i][0] == 'range_float'):
                new_arg_dic[i] = []
                temp_lst = np.linspace(float(x264_arg_dic[i][1]), float(x264_arg_dic[i][2]), 5, dtype=float)
                for j in temp_lst:
                    new_arg_dic[i].append(str(j))
            elif (x264_arg_dic[i][0] == 'range_integer'):
                new_arg_dic[i] = []
                temp_lst = np.linspace(int(x264_arg_dic[i][1]), int(x264_arg_dic[i][2]), 5, dtype=int)
                for k in temp_lst:
                    new_arg_dic[i].append(str(k))
            else:
                new_arg_dic[i] = x264_arg_dic[i]
    return new_arg_dic
            # print(f'arg_value:{x264_arg_dic[i]}')



def get_arg_all_subset(arg_list, arg_dic):
        # generate all combination of N items
        N = len(arg_list)
        # enumerate the 2**N possible combinations
        for i in range(2 ** N):
            arg_set = []
            for j in range(N):
                if (i >> j) % 2 == 1:
                    arg_set.append(arg_list[j])
            lists = []
            solid_list = []
            soft_list = []
            for k in arg_set:
                if k in arg_dic:
                    lists.append(arg_dic[k])
                    soft_list.append(k)
                else:
                    solid_list.append(k)

            for i in product(*lists):
                index = 0
                a =  list(i)
                for k in soft_list:
                    a.insert(index, k)
                    index +=2
                yield solid_list + a

def test_X264_argument(arg_lst, arg_dic,log_obj):
    test_iter = get_arg_all_subset(arg_lst, arg_dic)
    while True:
        #
        try:
            test_arg = next(test_iter)
            x_obj = X264_test(file_name_list[1], 'flv', test_arg, log_obj)
            x_obj()
        except AssertionError:
            print('It not be a good format or arg')
            continue
        except ValueError:
            print('this arg can not execute')
            print(f'arg:{test_arg}')
            continue
        except StopIteration:
            print('test finish')
            break

    log_obj.csv_flush()




if __name__ == '__main__':
    #更改目录
    subprocess.call(['mkdir', './temp'])
    subprocess.call(['cp', './'+file_name_list[1], './temp/' + file_name_list[1]])
    path =  os.path.join(os.getcwd(), 'temp')
    os.chdir(path)
    new_arg_dic = X264_arg_dic_process()
    my_log =  csv_log.csv_record('result.csv', x264_arg_lst)
    test_X264_argument(x264_arg_lst, new_arg_dic, log_obj=my_log)


