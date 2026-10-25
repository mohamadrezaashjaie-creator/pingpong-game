from kivy.app import App
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, Line, Ellipse
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from random import choice, uniform

class Table(Widget):
    def __init__(self, app, **kw):
        super().__init__(**kw)
        self.app=app; self.mode="bot"; self.score=[0,0]; self.paused=False; self.finished=False
        self.px=[.5,.5]; self.py=[.13,.87]; self.ball=[.5,.5]; self.v=[.24,.32]; self.touches={}
        Clock.schedule_interval(self.update,1/60); self.bind(pos=self.draw,size=self.draw)
    def start(self,mode):
        self.mode=mode; self.score=[0,0]; self.px=[.5,.5]; self.ball=[.5,.5]
        self.v=[choice([-1,1])*.24,choice([-1,1])*.32]; self.paused=False; self.finished=False; self.draw()
    def update(self,dt):
        if self.app.screen!="game" or self.paused or self.finished:return
        dt=min(dt,.03)
        if self.mode=="bot":
            d=self.ball[0]-self.px[1]; self.px[1]+=max(-.58*dt,min(.58*dt,d))
        self.ball[0]+=self.v[0]*dt; self.ball[1]+=self.v[1]*dt
        if self.ball[0]<.02:self.ball[0]=.02;self.v[0]=abs(self.v[0])
        if self.ball[0]>.98:self.ball[0]=.98;self.v[0]=-abs(self.v[0])
        for i,y in enumerate(self.py):
            if abs(self.ball[1]-y)<.035 and abs(self.ball[0]-self.px[i])<.13 and ((i==0 and self.v[1]<0) or (i==1 and self.v[1]>0)):
                self.v[1]*=-1.04; self.v[0]=max(-.48,min(.48,self.v[0]+(self.ball[0]-self.px[i])*.55))
        if self.ball[1]<-.02:self.score[1]+=1;self.reset_ball(1)
        if self.ball[1]>1.02:self.score[0]+=1;self.reset_ball(-1)
        if max(self.score)>=7:self.finished=True
        self.draw()
    def reset_ball(self, direction):
        self.ball=[.5,.5];self.v=[uniform(-.22,.22),direction*.32]
    def draw(self,*a):
        self.canvas.clear()
        with self.canvas:
            Color(.04,.38,.20,1);Rectangle(pos=self.pos,size=self.size)
            Color(1,1,1,1);Line(rectangle=(self.x+8,self.y+8,self.width-16,self.height-16),width=1.3)
            Line(points=[self.x+8,self.center_y,self.right-8,self.center_y],width=1)
            Line(circle=(self.center_x,self.center_y,min(self.width,self.height)*.09),width=1)
            for i,y in enumerate(self.py):
                Color(*( (.95,.18,.18,1) if i==0 else (.1,.85,.95,1) ))
                w=self.width*.23;h=max(10,self.height*.018)
                Rectangle(pos=(self.x+self.px[i]*self.width-w/2,self.y+y*self.height-h/2),size=(w,h))
            Color(1,1,1,1);r=min(self.width,self.height)*.014
            Ellipse(pos=(self.x+self.ball[0]*self.width-r,self.y+self.ball[1]*self.height-r),size=(2*r,2*r))
    def on_touch_down(self,t):
        if self.app.screen=="game" and self.collide_point(*t.pos) and not self.paused and not self.finished:
            side=0 if t.y<self.center_y else 1
            if self.mode=="bot" and side==1:return True
            self.touches[t.uid]=side;self.move_paddle(t,side);return True
        return super().on_touch_down(t)
    def on_touch_move(self,t):
        if t.uid in self.touches:self.move_paddle(t,self.touches[t.uid]);return True
        return super().on_touch_move(t)
    def on_touch_up(self,t):self.touches.pop(t.uid,None);return super().on_touch_up(t)
    def move_paddle(self,t,i):
        self.px[i]=max(.13,min(.87,(t.x-self.x)/max(1,self.width)));self.draw()

class PingPongApp(App):
    def build(self):
        self.title="Ping Pong";self.root=FloatLayout();self.screen="menu";self.table=Table(self)
        Window.bind(on_keyboard=self.key);self.menu();return self.root
    def clear(self):self.root.clear_widgets()
    def button(self,text,y,fn,w=.68,h=.09):
        b=Button(text=text,size_hint=(w,h),pos_hint={"center_x":.5,"center_y":y},font_size="18sp",bold=True,background_normal="",background_color=(.12,.25,.32,1))
        b.bind(on_release=lambda *_:fn());self.root.add_widget(b)
    def menu(self):
        self.screen="menu";self.clear()
        self.root.add_widget(Label(text="[b]PING PONG[/b]",markup=True,font_size="32sp",size_hint=(1,.18),pos_hint={"center_x":.5,"center_y":.78}))
        self.button("PLAY WITH BOT",.56,lambda:self.play("bot"))
        self.button("2 PLAYERS",.42,lambda:self.play("two"))
        self.root.add_widget(Label(text="First to 7 points wins",font_size="15sp",size_hint=(1,.08),pos_hint={"center_x":.5,"center_y":.28}))
    def play(self,mode):
        self.screen="game";self.clear();self.table.size_hint=(1,.78);self.table.pos_hint={"x":0,"y":.10};self.root.add_widget(self.table);self.table.start(mode)
        self.button("PAUSE / RESUME",.95,self.pause,.42,.07);self.button("RESTART",.87,lambda:self.table.start(self.table.mode),.30,.07);self.button("MENU",.04,self.menu,.30,.07)
        self.status=Label(text="",font_size="18sp",bold=True,size_hint=(.55,.07),pos_hint={"center_x":.5,"center_y":.81});self.root.add_widget(self.status)
        Clock.schedule_interval(self.status_update,.1)
    def status_update(self,dt):
        if self.screen!="game":return False
        s=self.table.score
        if self.table.finished:
            win="BOTTOM PLAYER WINS!" if s[0]>s[1] else ("YOU WIN!" if self.table.mode=="bot" else "TOP PLAYER WINS!")
            self.status.text=f"{s[0]} - {s[1]}  {win}"
        else:self.status.text=f"{s[0]} - {s[1]}"+("  PAUSED" if self.table.paused else "")
        return True
    def pause(self):
        if self.screen=="game" and not self.table.finished:self.table.paused=not self.table.paused
    def key(self,window,key,*args):
        if key==27 and self.screen=="game":self.menu();return True
        return False

if __name__=="__main__":PingPongApp().run()
