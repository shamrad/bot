from datetime import datetime, timedelta
import telepot
from telepot.delegate import pave_event_space, per_chat_id, create_open,  include_callback_query_chat_id
from .models import TeleUser,Word
from .form import TeleUserForm, WordForm
from telepot.namedtuple import ReplyKeyboardMarkup,KeyboardButton,ReplyKeyboardRemove,InlineKeyboardButton, InlineKeyboardMarkup
from django.db.models import Q
import random

TOKEN='333028480:AAG2EAmXyBfGqV4XYyD7iD7EEZnd6zvil78'


class Start(telepot.helper.ChatHandler):
    def __init__(self ,*args, **kwargs):
        super(Start, self).__init__(*args, **kwargs)
        self._id = 0
        self._answer = None
        self._answer_id=None
        self._score=0
        self._message_ind=None
        self._delete=0
        global key1

# state = 1  start
# state = 2  sabte loghat
# state = 3  sabte mani
# state = 4  liste loghat ha
# state = 5  moror



    def on_chat_message(self, msg):
        from_id = msg['from']['id']
        # self._sender.sendMessage(from_id)
        user=TeleUser.objects.filter(user_id=from_id)
        if user:
            a = TeleUser.objects.get(user_id=from_id)
            key1 = ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text='sabte loghate jadid'), KeyboardButton(text='moro loghat ha')],
                          [KeyboardButton(text='liste loghat ha')]],
                resize_keyboard=True, one_time_keyboard=True)
            if msg['text']=='/back':
                a.state = 1
                a.save()
                self.sender.sendMessage('user shekl greft, yeki az guzine ha ro entekhab konid', reply_markup=key1)

            else:

                if a.state==1:
                    if msg['text']=='sabte loghate jadid':
                        a.state =2
                        a.save()
                        self.sender.sendMessage('loghat vared konid, /back',reply_markup=ReplyKeyboardRemove(remove_keyboard=True))
                    elif msg['text']=='moro loghat ha':
                        wordscount = Word.objects.filter(teleuser=a).count()
                        key2=InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text='shoro moro', callback_data='shoro')],[InlineKeyboardButton(text='khoroj', callback_data='end')
                         ]])
                        send=self.sender.sendMessage('tedad e '+str(wordscount)+' loghat sabt karde eid',reply_markup=key2)
                        self._id=msg['from']['id']
                        self._message_ind=telepot.message_identifier(send)
                    elif msg['text']=='liste loghat ha':
                        list=Word.objects.filter(teleuser=a.pk)
                        n=0
                        for i in list:
                            n=n+1
                            text = '{count}- {word} '.format(count=n,word=i.word)
                            key= InlineKeyboardMarkup(inline_keyboard=[
                                [InlineKeyboardButton(text='details', callback_data=str(i.pk))]])
                            self.sender.sendMessage(text,reply_markup=key)

                        a.state=4
                        a.save()

                    else:
                        self.sender.sendMessage('user shekl greft, yeki az guzine ha ro entekhab konid', reply_markup=key1)
                        a.state=1
                        a.save()

                elif a.state==2:
                    form = WordForm(data={
                        'word': msg['text'],
                        'teleuser': a.pk,
                    })
                    if form.is_valid():
                        form.save()
                        self.sender.sendMessage('manira vared konid', reply_markup=ReplyKeyboardRemove(remove_keyboard=True))
                        a.state=3
                        a.save()
                    else:
                        self.sender.sendMessage(form.errors)

                elif a.state == 3:
                    word = Word.objects.filter(teleuser=a).last()
                    if word.meaning:
                        text='manie in loghat ghablan sabt shode ast: a%'%(word.meaning)
                        self.sender.sendMessage(text, reply_markup=key1)
                    else:
                        word.meaning=msg['text']
                        word.save()
                        a.state=2
                        a.save()
                        self.sender.sendMessage('loghat sabt shod, loghate badi ra vared konid, /back', reply_markup=key1)
                elif a.state==5:
                    a.state = 1
                    a.save()
                    self.close()

                else:
                    self.sender.sendMessage('yeki az guzine ha ro entekhab konid', reply_markup=key1)
                    a.state=1
                    a.save()



        else:

            form = TeleUserForm(data={
                'user_name': msg['from']['username'],
                'user_id': from_id,
                'first_name': msg['from']['first_name'],
                'state': 1,
            })
            if form.is_valid():
                form.save()
                key1 = ReplyKeyboardMarkup(
                    keyboard=[[KeyboardButton(text='sabte loghate jadid')]],
                    resize_keyboard=True)
                self.sender.sendMessage('user shekl greft, yeki az guzine ha ro entekhab konid',reply_markup=key1)
            else:
                self.sender.sendMessage(form.errors)


    def _show_next_question(self,msg):

        chat_id=telepot.glance(msg, flavor='callback_query')

        a = TeleUser.objects.get(user_id=msg['from']['id'])
        words=Word.objects.filter(teleuser=a).filter(Q(next_review_time__lte=datetime.now())|Q(next_review_time=None)).order_by('-next_review_time').last()
        if words:
            choice=Word.objects.exclude(pk=words.pk).order_by('?').all()[:3]
            list=[]
            for i in choice:
                list.append(i)
            answer=words.pk
            answer_meaning = words.meaning
            list.append(words)
            random.shuffle(list)
            question = '{word}  ' \
                       '1-{one} ' \
                       '2-{two} ' \
                       '3-{three} ' \
                       '4-{four} '.format(word=words.word,one=list[0].meaning,two=list[1].meaning,three=list[2].meaning,four=list[3].meaning)

            key3 = InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text=str(1), callback_data=str(list[0].pk)),InlineKeyboardButton(text=str(2), callback_data=str(list[1].pk)),
                InlineKeyboardButton(text=str(3), callback_data=str(list[3].pk)),InlineKeyboardButton(text=str(4), callback_data=str(list[2].pk))
                ]])

            new=bot.editMessageText(msg_identifier=self._message_ind,text=question,reply_markup=key3)
            # new=bot.editMessageText(msg_identifier=self._message_ind,text=l,reply_markup=key3)
            self._message_ind=telepot.message_identifier(new)
            # self.sender.sendMessage(question,reply_markup=key3)

        else:
            self.sender.sendMessage('shoma hich loghaty baraye moror nadaryd')

        return answer


    def on_callback_query(self, msg):
        query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
        a = TeleUser.objects.get(user_id=msg['from']['id'])
        if a.state==4:
            edit=Word.objects.get(pk=query_data)
            text='🚨word: {word}\n means:{means} \n'\
                 '? tedad sahih: {sahih}\n'\
                 'tedade ghalat: {ghalat}\n'\
                 'zamane tekrare badi {time}\n'.format(word=edit.word,
                                                     means=edit.meaning,sahih=edit.correct_answer,
                                                     ghalat=edit.wrong_answer,time=edit.next_review_time)
            self.sender.sendMessage(text)

        else:
            if query_data == 'shoro':
                count=Word.objects.filter(teleuser=a).count()
                if count>3:
                    bot.answerCallbackQuery(query_id, text='ogey')
                    a.state=5
                    a.save()
                    self._answer = self._show_next_question(msg=msg)
                else:
                    self.sender.sendMessage('baraye moro hadaghal bayad se kalame vared karde bashid')
                    self.sender.sendMessage('baraye edame yeki az gozine haye zir ra vared konid')



            elif query_data == 'end':
                a.state=1
                a.save()
                key1 = ReplyKeyboardMarkup(
                    keyboard=[[KeyboardButton(text='sabte loghate jadid'), KeyboardButton(text='moro loghat ha')],
                              [KeyboardButton(text='liste loghat ha')]],
                    resize_keyboard=True, one_time_keyboard=True)
                self.sender.sendMessage('az moro kharej shodid eki az guzine ha ro entekhab konid', reply_markup=key1)
                self.close()

            elif query_data== str(self._answer):
                days=[1,1,2,5,10,20,40]
                bot.answerCallbackQuery(query_id, text='afarin bari kala ')

                id=self._answer

                word=Word.objects.get(id=id)
                i=word.level
                if i<7:
                    word.next_review_time=datetime.now()+timedelta(days=days[i])
                else:
                    word.next_review_time = datetime.now() + timedelta(days=40)

                self._score= self._score+5
                word.level = word.level + 1
                word.correct_answer=word.correct_answer+1
                word.save()
                a.points=a.points+5
                a.save()
                bot.answerCallbackQuery(query_id, text='barik')
                self._answer = self._show_next_question(msg=msg)

            else:
                if self._answer==None:
                    self.sender.sendMessage('az aval')
                    a.state=1
                    a.save()
                else:
                    id = self._answer
                    word = Word.objects.get(id=id)
                    word.level=0
                    word.wrong_answer=+1
                    word.save()
                    bot.answerCallbackQuery(query_id, text='wrong ')


    def on__idle(self, event):
        from_id=event['_idle']['source']['id']
        a=TeleUser.objects.get(user_id=from_id)
        if a.state==5:
            a.state=1
            a.save()
            self.sender.sendMessage('time done')
            self._answer=None
            self.close()
        else:
            pass

            # bot.editMessageReplyMarkup(msg_identifier=self._message_ind, reply_markup=None)
    # def on_close(self, ex):
    #     key1 = ReplyKeyboardMarkup(
    #         keyboard=[[KeyboardButton(text='sabte loghate jadid'), KeyboardButton(text='moro loghat ha')],
    #                   [KeyboardButton(text='liste loghat ha')]],
    #         resize_keyboard=True, one_time_keyboard=True)
    #     # a=TeleUser.objects.get(user_id=self._id)
    #     # a.points=self._score
    #     text='score: {score}'.format(score=self._score)
    #     self.sender.sendMessage(text,reply_markup=key1)
    #     bot.editMessageReplyMarkup(msg_identifier=self._message_ind,reply_markup=None)


bot = telepot.DelegatorBot(TOKEN, [
    include_callback_query_chat_id(
    pave_event_space())(per_chat_id(), create_open, Start, timeout=10),
    # pave_event_space()(
        # per_callback_query_origin(), create_open, Test, timeout=10),
])
bot.message_loop(run_forever='Listening ...')
