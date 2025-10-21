import smtplib
import os
import json
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import parsedate_to_datetime
from datetime import datetime, timedelta
import poplib
from typing import Union, Optional
from pathlib import Path
from email import policy
from email.parser import BytesParser
from email.header import decode_header, make_header

class EmailUseType:
    def __init__(self, config_file_path: str = None) -> None:
        self.sender: Optional[str] = None
        self.user: Optional[str] = None
        self.passwd: Optional[str] = None
        self.receiver: Optional[str] = None
        if config_file_path is not None:
            self.load_emailInfo(config_file_path) 

    def load_emailInfo(self, file_path: str):
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
            # 提取 QQ_email_config 部分
            qq_email_config = data.get('QQ_email_config', {})

            # 提取 username、passwd 和 receiver
            self.sender = qq_email_config.get('username', self.sender)
            self.user = qq_email_config.get('username', self.user)
            self.passwd = qq_email_config.get('passwd', self.passwd)
            self.receiver = qq_email_config.get('receiver', self.receiver)
            
            if not all([self.sender, self.user, self.passwd, self.receiver]):
                print("警告:email 配置中的某些信息缺失。")
        except FileNotFoundError:
            print(f"文件 {file_path} 未找到。")
        except json.JSONDecodeError:
            print("文件内容不是有效的 JSON 格式。")
        except Exception as e:
            print(f"发生错误：{e}")

    def input_emailInfo(self, sender: str, passwd: str, receiver: str):
        self.sender = self.user = sender
        self.passwd = passwd
        self.receiver = receiver

    def check_emailInfo(self) -> None:
        print('----- Email Info -----')
        print(f"Sender: {self.sender}")
        print(f"User: {self.user}")
        print(f"Password: {self.passwd}")
        print(f"Receiver: {self.receiver}")


    def send_QQ_email_plain(self, email_title: str = 'Null', email_content: str = ''):
        "发送纯文本的qq邮件"
        sender = user = self.sender    # 发送方的邮箱账号
        passwd = self.passwd            # 授权码
        receiver = self.receiver        # 接收方的邮箱账号，不一定是QQ邮箱

        # 纯文本内容 
        msg = MIMEText(email_content, 'plain', 'utf-8')
        # From 的内容是有要求的，前面的abc为自己定义的 nickname，如果是ASCII格式，则可以直接写
        msg['From'] = user
        msg['To'] = receiver
        msg['Subject'] = email_title         # 点开详情后的标题


        try:
            # 建立 SMTP 、SSL 的连接，连接发送方的邮箱服务器
            smtp = smtplib.SMTP_SSL('smtp.qq.com', 465)
    
            # 登录发送方的邮箱账号
            smtp.login(user, passwd)
    
            # 发送邮件 发送方，接收方，发送的内容
            smtp.sendmail(sender, receiver, msg.as_string())
    
            print('邮件发送成功')
    
            smtp.quit()
        except Exception as e:
            print(e)
            print('发送邮件失败')

    def send_QQ_email_mul(self, email_title: str = 'Null', email_content: str = '', annex_path: str = ''):
        sender = user = self.sender    # 发送方的邮箱账号
        passwd = self.passwd            # 授权码
        receiver = self.receiver        # 接收方的邮箱账号，不一定是QQ邮箱
    
        content = MIMEMultipart()           # 创建一个包含多个部分的内容
        content['From'] = user
        content['To'] = receiver
        content['Subject'] = email_title
    
        # 添加文本内容
        text = MIMEText(email_content, 'plain', 'utf-8')
        content.attach(text)

        # 添加附件
        with open(annex_path, 'rb') as f:
            attachment = MIMEApplication(f.read())    # 读取为附件
            attachment.add_header('Content-Disposition', 'attachment', filename=os.path.basename(annex_path))
            content.attach(attachment)
    
        try:
            smtp = smtplib.SMTP_SSL('smtp.qq.com', 465)
            smtp.login(user, passwd)
            smtp.sendmail(sender, receiver, content.as_string())
            print('邮件发送成功')
        except Exception as e:
            print(e)
            print('发送邮件失败')

    def sanitize_folder_name(self, name):
        return ''.join(c for c in name if c.isalnum() or c in ('', '_', '-')).rstrip()

    def get_payload(self, email):
        if email.is_multipart():
            for part in email.iter_parts():
                content_type = part.get_content_type()
                content_disposition = part.get("Content-Disposition", "")
                
                if content_type == 'text/plain':
                    payload = part.get_payload(decode=True)
                    charset = part.get_content_charset() or 'utf-8'
                    try:
                        return payload.decode(charset), 'text', []
                    except (UnicodeDecodeError, TypeError):
                        return payload.decode('utf-8', errors='ignore'), 'text', []
                elif content_type == 'text/html':
                    payload = part.get_payload(decode=True)
                    charset = part.get_content_charset() or 'utf-8'
                    try:
                        return payload.decode(charset), 'html', []
                    except (UnicodeDecodeError, TypeError):
                        return payload.decode('utf-8', errors='ignore'), 'html', []
                elif 'attachment' in content_disposition:
                    filename = part.get_filename()
                    if filename:
                        extension = filename.split('.')[-1]
                        return part.get_payload(decode=True), 'image', [extension]
        else:
            content_type = email.get_content_type()
            if content_type == 'text/plain':
                payload = email.get_payload(decode=True)
                charset = email.get_content_charset() or 'utf-8'
                try:
                    return payload.decode(charset), 'text', []
                except (UnicodeDecodeError, TypeError):
                    return payload.decode('utf-8', errors='ignore'), 'text', []
            elif content_type == 'text/html':
                payload = email.get_payload(decode=True)
                charset = email.get_content_charset() or 'utf-8'
                try:
                    return payload.decode(charset), 'html', []
                except (UnicodeDecodeError, TypeError):
                    return payload.decode('utf-8', errors='ignore'), 'html', []
        
        return '', 'unknown', []
    
    def get_email_and_save(self):
        sender = user = self.sender    # 发送方的邮箱账号
        passwd = self.passwd            # 授权码
        # 连接到POP3服务器
        pop_server = poplib.POP3_SSL('pop.qq.com', 995)
        pop_server.user(sender)
        pop_server.pass_(passwd)
        
        # 获取邮箱中的邮件信息
        num_emails = len(pop_server.list()[1])
        
        # 计算7天前的日期
        seven_days_ago = datetime.now() - timedelta(days=7)
            
        # 确保 seven_days_ago 是 offset-naive
        seven_days_ago = seven_days_ago.replace(tzinfo=None)

        # 遍历每封邮件
        for i in range(num_emails):
            # 获取邮件内容
            response, lines, octets = pop_server.retr(i + 1)
            email_content = b'\r\n'.join(lines)
        
            # 解析邮件内容
            email_parser = BytesParser(policy=policy.default)
            email = email_parser.parsebytes(email_content)
        
            # 解析邮件头部信息
            email_from = email.get('From').strip()
            email_from = str(make_header(decode_header(email_from)))

            try:        
                date_str = email.get('Date')
                # 解析邮件日期
                email_date = parsedate_to_datetime(date_str)
                # 确保 email_date 是 offset-naive
                email_date = email_date.replace(tzinfo=None)
            except (TypeError, ValueError):
                continue  # 如果邮件没有日期，跳过

            # 只处理最近7天内的邮件
            if email_date < seven_days_ago:
                continue

            if email_from:
                subject = email.get('Subject').strip()
                decoded_subject = str(make_header(decode_header(subject))) if subject else 'No Subject'

                email_body, body_type, *extras = self.get_payload(email)
                
                safe_folder_name = self.sanitize_folder_name(email_from)
                safe_subject = self.sanitize_folder_name(decoded_subject)

                print("------------------")
                print("From:", email_from)
                print("Subject:", decoded_subject)
                print("Body Type:", body_type)

                if body_type == 'text':
                    print("Body:", email_body)
                elif body_type == 'html':
                    directory = safe_folder_name
                    if not os.path.exists(directory):
                        os.makedirs(directory)
                    with open(f'{directory}/{safe_subject}.html', 'w') as f:
                        f.write(email_body)
                elif body_type == 'image':
                    directory = safe_folder_name
                    if not os.path.exists(directory):
                        os.makedirs(directory)
                    image_data = email_body
                    image_extension = extras[0] if extras else 'png'
                    with open(f'{directory}/{safe_subject}.{image_extension[0]}', 'wb') as f:
                        f.write(image_data)
            else:
                continue  # 跳过缺失发件人的邮件
        # 关闭连接
        pop_server.quit()

if __name__ =='__main__':
    email_use = EmailUseType()
    email_use.check_emailInfo()
