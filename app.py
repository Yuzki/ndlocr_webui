import click
import json
import os
import sys

from cli.core import OcrInferencer
from cli.core import utils

import gradio as gr
from PIL import Image
import shutil
import zipfile
from pathlib import Path
from pdf2image import convert_from_path



class OcrProcess:
    def __init__(self):
        self.tmp_dir = '/root/ocr_cli/tmp'
        self.img_dir = os.path.join(self.tmp_dir, 'img')
    
    # 入出力ファイルを格納する一時ディレクトリの作成
    def make_tmp_dir(self):
        os.mkdir(self.tmp_dir)
        os.mkdir(self.img_dir)
    
    # 一時ディレクトリの削除
    def remove_tmp_dir(self):
        shutil.rmtree(self.tmp_dir)
    
    # 単一画像の保存
    def save_single_image(self, input_image):
        # 受け取った画像を /root/ocr_cli/tmp/img に保存する
        image = Image.fromarray(input_image.astype('uint8'), 'RGB')
        self.image_name = 'image.jpg'
        self.image_path = os.path.join(self.img_dir, self.image_name)
        image.save(self.image_path)

        print(f'Image is saved: {self.image_path}')
    
    # 複数画像の保存
    def save_multiple_image(self, input_images):
        for i, input_image in enumerate(input_images):
            image_name = os.path.basename(input_image.name)
            image_path = os.path.join(self.img_dir, image_name)

            with open(input_image.name, 'rb') as image_file:
                image = Image.open(image_file)
                image.save(image_path)

        print(f'Images are saved: {self.img_dir}')

    # pdfから画像に変換し画像を保存
    def save_image_from_pdf(self, input_pdf):
        images = convert_from_path(input_pdf.name)
        for i, image in enumerate(images):
            output_file = os.path.join(self.img_dir, f'{os.path.basename(input_pdf.name)}_{str(i+1).zfill(4)}.jpg')
            image.save(output_file, 'JPEG')

        print(f'PDF is converted and images are saved: {self.img_dir}')
    

    def infer(self, config_file, proc_range, save_image, save_xml, input_structure, dump):
        
        if input_structure == 'f':
            input_root = self.image_path
        elif input_structure == 's':
            input_root = self.tmp_dir
        
        self.output_root = os.path.join(self.tmp_dir, 'output')

        
        cfg = {
            'input_root': input_root,
            'output_root': self.output_root,
            'config_file': config_file,
            'proc_range': proc_range,
            'save_image': save_image,
            'save_xml': save_xml,
            'dump': dump,
            'input_structure': input_structure
        }

        # check if input_root exists
        if not os.path.exists(input_root):
            print('INPUT_ROOT not found :{0}'.format(input_root), file=sys.stderr)
            exit(0)

        # parse command line option
        infer_cfg = utils.parse_cfg(cfg)
        if infer_cfg is None:
            print('[ERROR] Config parse error :{0}'.format(input_root), file=sys.stderr)
            exit(1)

        # prepare output root derectory
        infer_cfg['output_root'] = utils.mkdir_with_duplication_check(infer_cfg['output_root'])

        # save inference option
        with open(os.path.join(infer_cfg['output_root'], 'opt.json'), 'w') as fp:
            json.dump(infer_cfg, fp, ensure_ascii=False, indent=4,
                    sort_keys=True, separators=(',', ': '))

        # do inference
        inferencer = OcrInferencer(infer_cfg)
        inferencer.run()
    
    def get_text(self):
        pid = os.path.splitext(os.path.basename(self.image_name))[0]
        txt_path = os.path.join(self.output_root, pid, 'txt', f'{pid}_main.txt')
        with open(txt_path, 'r', encoding='utf-8') as f:
            text = f.read()

        return text
    
    def zip_directory(self, zip_file):
        with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(self.output_root):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(file_path, self.output_root))




def ocr_single_image(input_image, config_file, proc_range, save_image, save_xml, dump):

    ocr = OcrProcess()

    ocr.make_tmp_dir()

    ocr.save_single_image(input_image)

    # infer
    input_structure = 'f'
    ocr.infer(config_file, proc_range, save_image, save_xml, input_structure, dump)
    
    # outputs
    text = ocr.get_text()
    ocr.zip_directory('result.zip')

    ocr.remove_tmp_dir()

    return text, 'result.zip'


def ocr_multiple_image(input_images, config_file, proc_range, save_image, save_xml, dump):
    ocr = OcrProcess()

    ocr.make_tmp_dir()

    ocr.save_multiple_image(input_images)

    input_structure = 's'
    ocr.infer(config_file, proc_range, save_image, save_xml, input_structure, dump)

    ocr.zip_directory('result.zip')

    ocr.remove_tmp_dir()

    return 'result.zip'


def ocr_pdf(input_pdf, config_file, proc_range, save_image, save_xml, dump):
    ocr = OcrProcess()

    ocr.make_tmp_dir()

    ocr.save_image_from_pdf(input_pdf)

    input_structure = 's'
    ocr.infer(config_file, proc_range, save_image, save_xml, input_structure, dump)
    
    ocr.zip_directory('result.zip')

    ocr.remove_tmp_dir()

    return 'result.zip'


def main():

    with gr.Blocks() as interface:
        gr.Markdown('入力形式を選んでください')

        with gr.Tabs():
            with gr.TabItem('単一画像'):
                i2t_inputs = [
                    # input_image
                    gr.Image(label='入力画像'),
                    # config_file
                    gr.Textbox(label='設定ファイル', value='config.yml'),
                    # proc_range
                    gr.Textbox(label='部分実行(0: ノド元分割, 1: 傾き補正, 2: レイアウト抽出, 3: 文字認識(OCR))', value='0..3'),
                    # save_image
                    gr.Checkbox(label='画像保存'),
                    # save_xml
                    gr.Checkbox(label='XML保存'),
                    # dump
                    gr.Checkbox(label='dump')
                ]
                i2t_outputs = [gr.Textbox(label='結果'), gr.File(label='出力ファイル (ZIP)')]
                i2t_button = gr.Button('OCR開始')
            
            with gr.TabItem('複数画像'):
                d2t_inputs = [
                    # input_image
                    gr.File(label='入力画像', file_count='multiple', file_types=['image']),
                    # config_file
                    gr.Textbox(label='設定ファイル', value='config.yml'),
                    # proc_range
                    gr.Textbox(label='部分実行(0: ノド元分割, 1: 傾き補正, 2: レイアウト抽出, 3: 文字認識(OCR))', value='0..3'),
                    # save_image
                    gr.Checkbox(label='画像保存'),
                    # save_xml
                    gr.Checkbox(label='XML保存'),
                    # dump
                    gr.Checkbox(label='dump')
                ]
                d2t_outputs = gr.File(label='出力ファイル (ZIP)')
                d2t_button = gr.Button('OCR開始')
            
            with gr.TabItem('PDF'):
                p2t_inputs = [
                    # input_pdf
                    gr.File(label='入力PDF', file_types=[".pdf"]),
                    # config_file
                    gr.Textbox(label='設定ファイル', value='config.yml'),
                    # proc_range
                    gr.Textbox(label='部分実行(0: ノド元分割, 1: 傾き補正, 2: レイアウト抽出, 3: 文字認識(OCR))', value='0..3'),
                    # save_image
                    gr.Checkbox(label='画像保存'),
                    # save_xml
                    gr.Checkbox(label='XML保存'),
                    # dump
                    gr.Checkbox(label='dump')
                ]
                p2t_outputs = gr.File(label='出力ファイル (ZIP)')
                p2t_button = gr.Button('OCR開始')
            
        i2t_button.click(ocr_single_image, inputs=i2t_inputs, outputs=i2t_outputs)
        d2t_button.click(ocr_multiple_image, inputs=d2t_inputs, outputs=d2t_outputs)
        p2t_button.click(ocr_pdf, inputs=p2t_inputs, outputs=p2t_outputs)


    interface.launch()


if __name__ == '__main__':
    main()