from datetime import datetime, timedelta
import telepot
from telepot.delegate import pave_event_space, per_chat_id, create_open, per_callback_query_origin, include_callback_query_chat_id
from .models import TeleUser,Word
from .form import TeleUserForm, WordForm
from telepot.namedtuple import ReplyKeyboardMarkup,KeyboardButton,ReplyKeyboardRemove,InlineKeyboardButton, InlineKeyboardMarkup
from django.db.models import Q


TOKEN='333028480:AAG2EAmXyBfGqV4XYyD7iD7EEZnd6zvil78'


class Start(telepot.helper.ChatHandler):
    key1 = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text='sabte loghate jadid'), KeyboardButton(text='moro loghat ha')],
                  [KeyboardButton(text='liste loghat ha')]],
        resize_keyboard=True, one_time_keyboard=True)
    def __init__(self ,*args, **kwargs):
        super(Start, self).__init__(*args, **kwargs)
        self._count = 0
        self._answer = None
        self._answer_id=None


    def on_chat_message(self, msg):
        from_id = msg['from']['id']
        # self._sender.sendMessage(from_id)
        user=TeleUser.objects.filter(user_id=from_id)
        if user:
            a=TeleUser.objects.get(user_id=from_id)
            key1 = ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text='sabte loghate jadid'), KeyboardButton(text='moro loghat ha')],[KeyboardButton(text='liste loghat ha')]],
                resize_keyboard=True,one_time_keyboard=True)
            if a.state==1:

                if msg['text']=='sabte loghate jadid':
                    a.state=2
                    a.save()
                    self.sender.sendMessage('loghat vared konid, /back',reply_markup=ReplyKeyboardRemove(remove_keyboard=True))
                elif msg['text']=='moro loghat ha':
                    wordscount = Word.objects.filter(teleuser=a).count()
                    key2=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text='shoro moro', callback_data='shoro')],[InlineKeyboardButton(text='khoroj', callback_data='end')
                     ]])
                    self.sender.sendMessage('tedad e '+str(wordscount)+' loghat sabt karde eid',reply_markup=key2)

                elif msg['text']=='liste loghat ha':
                    list=Word.objects.filter(teleuser=a.pk)
                    n=0
                    for i in list:

                        n=n+1
                        text = '{count}- {word} '.format(count=n,word=i.word)
                        key= InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text=i.meaning, callback_data=i.meaning)]
                        ])
                        self.sender.sendMessage(text,reply_markup=key)

                    a.state=4
                    a.save()

                else:
                    self.sender.sendMessage('user shekl greft, yeki az guzine ha ro entekhab konid', reply_markup=key1)
                    a.state=1
                    a.save()

            elif a.state==2:
                if msg['text']=='/back':
                    a.state=1
                    a.save()
                    self.sender.sendMessage('user shekl greft, yeki az guzine ha ro entekhab konid', reply_markup=key1)
                else:

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
                    a.state=1
                    a.save()
                    self.sender.sendMessage('baraye edame yeki az gozine haye zir ra vared konid', reply_markup=key1)

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
                list.append(InlineKeyboardButton(text=i.meaning, callback_data=str(i.meaning)))

            answer=words.pk
            answer_meaning = words.meaning
            list.append(InlineKeyboardButton(text=answer_meaning, callback_data=str(answer)))


            question = words.word
            key3 = InlineKeyboardMarkup(inline_keyboard=[
                list])
            self.sender.sendMessage(question,reply_markup= key3  )
            # self.sender.sendMessage(words.next_review_time,reply_markup= key3  )
        else:
            self.sender.sendMessage('shoma hich loghaty baraye moror nadaryd')

        return answer


    def on_callback_query(self, msg):
        query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
        a = TeleUser.objects.get(user_id=msg['from']['id'])
        if a.state==4:
            edit=Word.objects.get(meaning=str(query_data))
            
            text='word: {word} means:{means} tedad sahih: {sahih}, tedade ghalat: {ghalat}' \
                 'zamane tekrare badi {time}'.format(word=edit.word,means=edit.meaning,sahih=edit.correct_answer,ghalat=edit.wrong_answer,time=edit.next_review_time)
            self.sender.sendMessage(text)

        else:
            if query_data == 'shoro':
                count=Word.objects.filter(teleuser=a).count()
                if count>3:
                    bot.answerCallbackQuery(query_id, text='ogey')
                    self._answer = self._show_next_question(msg=msg)
                else:
                    self.sender.sendMessage('baraye moro hadaghal bayad se kalame vared karde bashid')
                    self.sender.sendMessage('baraye edame yeki az gozine haye zir ra vared konid')



            elif query_data == 'end':
                key1 = ReplyKeyboardMarkup(
                    keyboard=[[KeyboardButton(text='sabte loghate jadid'), KeyboardButton(text='moro loghat ha')],
                              [KeyboardButton(text='liste loghat ha')]],
                    resize_keyboard=True, one_time_keyboard=True)
                self.sender.sendMessage('az moro kharej shodid eki az guzine ha ro entekhab konid', reply_markup=key1)


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

                word.level = word.level + 1
                word.correct_answer=word.correct_answer+1
                word.save()
                bot.answerCallbackQuery(query_id, text='barik')
                self._answer = self._show_next_question(msg=msg)
            else:
                if self._answer==None:
                    self.sender.sendMessage('az aval')
                else:
                    id = self._answer
                    word = Word.objects.get(id=id)
                    word.level=0
                    word.wrong_answer=+1
                    word.save()
                    bot.answerCallbackQuery(query_id, text='wrong ')




bot = telepot.DelegatorBot(TOKEN, [
    include_callback_query_chat_id(
    pave_event_space())(per_chat_id(), create_open, Start, timeout=30),
    # pave_event_space()(
        # per_callback_query_origin(), create_open, Test, timeout=10),
])
bot.message_loop(run_forever='Listening ...')
