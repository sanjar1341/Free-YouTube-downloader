from tkinter import Tk,Canvas,Entry,StringVar,messagebox,PhotoImage
from pytube import YouTube
from PIL import ImageTk,Image
from os.path import exists,join,dirname
from os import mkdir
from os import remove
from io import BytesIO
from requests import get
from threading import Thread
from datetime import datetime
import subprocess
from tkinter.filedialog import askdirectory
from configparser import ConfigParser

class Progressbar:
    def __init__(self,parent:Canvas,x,y,width=200,height=7,bg='#dcdcdc',outlinecolor='#969696',fg='#3ec747') -> None:
        self.parent=parent
        self.x=x
        self.y=y
        self.width=width
        self.height=height
        self.bg=bg
        self.fg=fg
        self.filesize=0
        self.download_size=0
        self.df=0
        self.start=datetime.now()
        self.outlinecolor=outlinecolor
        self.bgr=parent.create_rectangle(x,y,x+width,y+height,fill=bg,outline=outlinecolor)
        self.frg=parent.create_rectangle(x,y,x,y+height,fill=fg,outline=outlinecolor)
        self.flabel=parent.create_text(x+width+3,y-3,text="0 % 0 Mb/s",anchor='nw',font=('consolas',height),fill='#3ec747')
    


    def progress_callback(self,stream, chunk, bytes_remaining):
        size=stream.filesize
        t=datetime.now()-self.start
        self.start=datetime.now()
        t=t.seconds+t.microseconds/1000000
        ds=size-bytes_remaining-self.df
        self.download_size+=ds
        spd=ds/t/1024/1024
        spd=round(spd,1)
        self.df=size-bytes_remaining
        process=self.download_size/self.filesize
        self.setvalue(process,spd)
        



    def setvalue(self,value,speed):
        
        self.parent.coords(self.frg,[self.x,self.y,self.x+self.width*value,self.y+self.height])
        self.parent.itemconfig(self.flabel,text=f'{int(value*1000)/10} % {speed} Mb/s')
    def clear(self):
        self.parent.coords(self.frg,[self.x,self.y,self.x,self.y])
        self.filesize=0
        self.df=0
        self.download_size=0




class app(Tk):
    def __init__(self):
        super().__init__()
        self.iconbitmap(r'rasm.ico')
        self.resizable(0,0)
        self.configure(bg='#282828')
        self.title("Free YouTube downloader")
        #self.iconbitmap(r'icon.ico')
        self.tasks=None
        self.vid_itags={'144p':None,'240p':None,'360p':None,'480p':None,'720p':None,'1080p':None}
        self.audio_itag=None
        self.resolutions=['144p','240p','360p','480p','720p','1080p']
        self.delete_items=[]
        # try:
        
        # except Exception as e:
        #     messagebox.showerror('Error',e)
        
        
        

        # create url input box
        self.url=StringVar()
        self.url_input=Entry(self,width=40,font=("Consolas",11),foreground="blue",textvariable=self.url,highlightbackground = "#0c10f0", highlightcolor= "#0c10f0",highlightthickness=2,relief='flat')
        self.url_input.grid(row=0,column=0,padx=4,pady=4)
        self.url.trace_add('write',self.url_changed)

        # create canvas for you tube
        self.picturebox=Canvas(self,background='#3d3c3c',height=410,highlightthickness=0,width=263)
        self.picturebox.grid(row=1,column=0,sticky="WESN",padx=2,pady=1)
        y0=230
        y1=250
        self.picturebox.create_rectangle(6,2,325,165,fill='#414141',activeoutline='red')
        
        self.buttons={'144p':None,'240p':None,'360p':None,'480p':None,'720p':None,'1080p':None,'mp3':None}
        for i in self.resolutions:
            self.picturebox.create_rectangle(3,y0,328,y1,fill='#464646',outline='#288f18')
            self.buttons[i]=self.picturebox.create_text(300,y0,text='⇩',font=('consolas',12,'bold','roman','underline'),fill='#e9f0e9',anchor='nw',activefill='#ff0000',state='disabled')
            self.picturebox.tag_bind(self.buttons[i],'<ButtonPress-1>',lambda e:Thread(target=self.download,args=(e,)).start())
            y0+=20
            y1+=20
        self.picturebox.create_rectangle(3,y0,328,y1,fill='#464646',outline='#288f18')
        self.buttons['mp3']=self.picturebox.create_text(300,y0,text='⇩',font=('consolas',12,'bold','roman','underline'),fill='#e9f0e9',anchor='nw',activefill='#ff0000',state='disabled')
        self.picturebox.tag_bind(self.buttons['mp3'],'<ButtonPress-1>',lambda e:Thread(target=self.download,args=(e,)).start())

        self.progressbar=Progressbar(self.picturebox,x=3,y=380,height=10,width=210)
        

        self.status=self.picturebox.create_text(3,395,text='normal',anchor='nw')
        
        
        self.url_input.focus()
        self.form_load()
        self.eye=ImageTk.PhotoImage(Image.open("eye.png").resize((24,24),Image.ANTIALIAS))     
        self.images=[]
        self.picturebox.create_image(25,178,image=self.eye)
        


    def form_load(self):
        self.current_path=dirname(__file__)

        i=len(self.current_path)-1
        while i>0 and self.current_path[i]!='\\':
            i-=1
        self.current_path=self.current_path[0:i]
        d=ConfigParser()
        self.dw=join(self.current_path,'Downloads')
        
        if exists(self.dw)==0:
            mkdir(self.dw)
        if exists(path=self.current_path+'\\settings.ini'):
            d.read(self.current_path+'/settings.ini')
            if 'download_path' in d.sections():
                if 'name' in d['download_path']:
                    self.dw=d['download_path']['name']
                else:
                    d['download_path']={}
                    d['download_path']['name']=self.dw
                    with open(self.current_path+'/settings.ini','w') as fl:
                        d.write(fl)
            else:
                d['download_path']={}
                d['download_path']['name']=self.dw
                with open(self.current_path+'/settings.ini','w') as fl:
                    d.write(fl)
                    print(fl.name)
        else:
            d['download_path']={}
            d['download_path']['name']=self.dw
            with open(self.current_path+'/settings.ini','w') as fl:
                d.write(fl)
        if len(self.dw)<30:
            self.dowmload_path=self.picturebox.create_text(325,395,text=self.dw,anchor='ne',activefill='#cccac6')
        else:
            self.dowmload_path=self.picturebox.create_text(325,395,text='...'+self.dw[-30:],anchor='ne',activefill='#cccac6')
        self.picturebox.tag_bind(self.dowmload_path,'<ButtonPress-1>',self.download_path_change)


    def download_path_change(self,e):
        p=askdirectory(initialdir=self.dw)
        if p!=None and p!='':
            d=ConfigParser()
            d['download_path']={}
            d['download_path']['name']=p
            with open(self.current_path+'\\settings.ini','w') as fl:
                d.write(fl)

            self.dw=p
            if len(self.dw)<30:
                self.picturebox.itemconfig(self.dowmload_path,text=self.dw)
            else:
                self.picturebox.itemconfig(self.dowmload_path,text='...'+self.dw[-30:])


    def url_changed(self,a,b,c):
        
        try:
            self.yt=YouTube(self.url.get())
            self.yt.register_on_progress_callback(self.progressbar.progress_callback)
            self.url_input.config(highlightbackground='#1ca813',highlightcolor='#1ca813')
            t=Thread(target=self.url_write)
            t.start()
            
            
            self.tasks=t
            self.url_input.config(state='disabled')

        except:
            self.url_input.config(highlightbackground = "#0c10f0", highlightcolor= "#0c10f0")
            self.url_input.config(state='normal')
        


    def clear(self):
        
        self.images.clear()
        
        for i in self.delete_items:
            self.picturebox.delete(i)
        self.delete_items=[]
        self.vid_itags={'144p':None,'240p':None,'360p':None,'480p':None,'720p':None,'1080p':None}

    

    def url_write(self,n=0):
        self.hide_buttons()
        if n>4:
            self.url_input.config(state='normal')
            return
        
        try:
            self.picturebox.itemconfig(self.status,text='initializing...')
            views=self.get_views()
            delta=self.get_time_ago()
            title=self.yt.title
            if len(title)>40:
                title=title[0:40]+'\n'+title[40:]

            self.get_image()
            self.picturebox.create_image(6,2,image=self.images[len(self.images)-1][0],anchor='nw')
            id=self.picturebox.create_text(47,170,text=f'{views} просмотров {delta} назад',fill='#C3BFDC',font=('sans-serif',9),anchor='nw')
            self.delete_items.append(id)
            id=self.picturebox.create_text(6,185,text=title,font=('sans-serif',11,'bold'),anchor='nw')
            self.delete_items.append(id)
            
            self.streams=self.yt.streams.filter(file_extension='mp4',type='video')
            for i in self.streams:
                try:
                    if self.vid_itags[i.resolution]==None:
                        
                        self.vid_itags[i.resolution]=i
                except:
                    pass
            y0=230
            y1=250
            self.audio_itag=self.yt.streams.get_audio_only()
            print(self.audio_itag.default_filename)

            for i in self.vid_itags:
                if self.vid_itags[i]!=None:
                    print(self.vid_itags[i])
                    size=self.bit_convert(self.vid_itags[i].filesize)
                    if self.vid_itags[i].is_progressive==False:
                        size=self.bit_convert(self.vid_itags[i].filesize+self.audio_itag.filesize)
                    id=self.picturebox.create_text(4,y0,text=f'{self.vid_itags[i].resolution}\t\t{self.vid_itags[i].fps}fps\t\t{size}',anchor='nw',fill='#e4e6ed',font=('consolas',10))
                    self.delete_items.append(id)
                    self.picturebox.itemconfig(self.buttons[self.vid_itags[i].resolution],state='normal')
                    
                    
                y0+=20
                y1+=20
            if self.audio_itag!=None:
                size=self.bit_convert(self.audio_itag.filesize)
                
                id=self.picturebox.create_text(4,y0,text=f'mp3\t\t{self.audio_itag.abr}\t\t{size}',anchor='nw',fill='#e4e6ed',font=('consolas',10))
                self.delete_items.append(id)
                self.picturebox.itemconfig(self.buttons['mp3'],state='normal')
                
                
                y0+=20
                y1+=20
            self.url_input.config(state='normal')
            self.picturebox.itemconfig(self.status,text='normal')
            
        except Exception as e:
            print(e)
            self.url_write(n=n+1)



    def download(self,e)->None:
        self.picturebox.itemconfig(self.status,text='Connecting...')
        self.hide_buttons()
        self.progressbar.clear()
        self.url_input.config(state='disabled')
        a1=228
        i=0
        while a1<=e.y:
            a1+=20
            i+=1
        
        if i<7:
            vid=self.vid_itags[self.resolutions[i-1]]
            if vid.is_progressive==False:
                self.progressbar.start=datetime.now()
                self.progressbar.filesize=vid.filesize+self.audio_itag.filesize
                self.picturebox.itemconfig(self.status,text='downloading...')
                vid.download(filename='video.mp4',output_path=self.dw)
                self.progressbar.df=0
                self.audio_itag.download(filename='audio.mp4',output_path=self.dw)
                self.picturebox.itemconfig(self.status,text='merging..')
                subprocess.call(f'ffmpeg -i "{self.dw}//video.mp4" -i "{self.dw}//audio.mp4" -c:v copy -c:a copy "{self.dw}//{self.audio_itag.default_filename}"',shell=1)
                remove(self.dw+'//audio.mp4')
                remove(self.dw+'//video.mp4')

                self.picturebox.itemconfig(self.status,text='Complete')
                messagebox.showinfo('Complete','Downloading complete')
            else:
                self.progressbar.start=datetime.now()
                self.progressbar.filesize=vid.filesize
                self.picturebox.itemconfig(self.status,text='downloading...')
                vid.download(output_path=self.dw)
                self.picturebox.itemconfig(self.status,text='Complete')
                messagebox.showinfo('Complete','Downloading complete')
        else:
            self.picturebox.itemconfig(self.status,text='downloading...')
            self.progressbar.filesize=self.audio_itag.filesize
            self.progressbar.start=datetime.now()
            self.audio_itag.download(filename=self.audio_itag.default_filename[:-3]+".mp3",output_path=self.dw)
        self.url_input.config(state='normal')
        self.show_buttons()
        self.picturebox.itemconfig(self.status,text='Complete')
        #messagebox.showinfo('Complete','Downloading complete')
        

                
    def get_views(self):
        views=self.yt.views
        bkr=['','тыс','млн','млрд']
        i=0
        while views>1000:
            views/=1000
            i+=1
        return f'{round(views,2)} {bkr[i]}'
    
    def get_time_ago(self):
        current_date=datetime.now()
        publish_date=self.yt.publish_date
        if current_date.year>publish_date.year:
            return f'{current_date.year-publish_date.year} лет'
        elif current_date.month>publish_date.month:
            return f'{current_date.month-publish_date.month} месяцев'
        elif current_date.day>publish_date.day:
            return f'{current_date.day-publish_date.day} дней'
        elif current_date.hour>publish_date.hour:
            return f'{current_date.hour-publish_date.hour} часов'
        elif current_date.minute>publish_date.minute:
            return f'{current_date.minute-publish_date.minute} минут'
        else:
            return f'{current_date.second-publish_date.second} секунд'

    def bit_convert(self,value):
        if value<=0:
            return '0 b'
        bit=[' b',' kb',' mb',' gb']

        i=0

        while value>1024:
            value/=1024
            i+=1
        return str(round(value,1))+bit[i]
        
    def get_image(self):
        img_bytes=get(self.yt.thumbnail_url).content
        img1=Image.open(BytesIO(img_bytes))
        img2=img1.resize((319,163))
        img=ImageTk.PhotoImage(img2)
        self.clear()
        self.images.append([img,self.yt.video_id])
        
    def hide_buttons(self):
        for i in self.buttons:
            self.picturebox.itemconfig(self.buttons[i],state='disabled')
        
    def show_buttons(self):
        for i in self.vid_itags:
            if self.vid_itags[i]!=None:
                self.picturebox.itemconfig(self.buttons[i],state='normal')



if __name__=='__main__':
    app().mainloop()