import nltk
import pandas as pd
import string
import re

from nltk import word_tokenize, FreqDist
from nltk.corpus import stopwords
from pyecharts import options
from pyecharts.charts import Page, WordCloud, Pie, Bar, Timeline
from pyecharts.components import Table
from pyecharts.globals import SymbolType


class UserData:
    def __init__(self, username, guild_id, user_data):
        self.username = username
        self.guild_id = guild_id
        self._label_to_emotion = {
            "neutral": "Нейтрально",
            "positive": "Радость",
            "sad": "Грусть",
            "angry": "Злость",
            "other": "Другое"
        }
        self.results_page = self._generate_page(user_data)

    @staticmethod
    def _preprocess(text_list):
        text = " ".join(map(str, text_list))
        text = text.lower()
        spec_chars = string.punctuation + '«»\t—…’'
        text = "".join([ch for ch in text if ch not in spec_chars])
        text = re.sub('\n', ' ', text)
        russian_stopwords = stopwords.words("russian")
        text_tokens = word_tokenize(text)
        text_tokens = [token.strip() for token in text_tokens if token not in russian_stopwords]
        text = nltk.Text(text_tokens)

        return text

    def _wordcloud(self, data):
        tokenized_text = self._preprocess(data.text)
        top_100_words = FreqDist(tokenized_text).most_common(100)

        wordcloud = WordCloud() \
            .add("", top_100_words, shape=SymbolType.RECT, word_size_range=[20, 70], width="50%", height="500") \
            .set_global_opts(title_opts=options.TitleOpts(title="Частота употребления слов"))

        return wordcloud

    def _emotions_duration_pie(self, data):
        data = data.drop(columns=["text", "timestamp"])
        data = data.groupby("emotion")["duration"].sum()
        keys = data.index.tolist()
        keys = map(lambda x: self._label_to_emotion[x], keys)
        values = data.values.tolist()
        values = map(lambda x: round(x), values)

        chart = Pie(init_opts=options.InitOpts(width="50%")) \
            .add("Длительность в секундах",
                 [list(z) for z in zip(keys, values)],
                 radius=["30%", "75%"],
                 rosetype="radius"
                 ) \
            .set_global_opts(title_opts=options.TitleOpts(title="Длительность эмоций"),
                             legend_opts=options.LegendOpts(is_show=False)) \
            .set_series_opts(label_opts=options.LabelOpts(formatter="{b}: {d}%"))

        return chart

    def _emotions_timeline(self, data):
        data = data.drop(columns="timestamp")
        total_time = data.duration.sum()
        n_intervals = int(total_time) // 1200 + 1
        data['cumulative_duration'] = data.duration.cumsum()
        timeline = Timeline(init_opts=options.InitOpts(width="100%", height="200px"))
        for i in range(0, n_intervals):
            bar = Bar(init_opts=options.InitOpts()) \
                .add_xaxis([""]) \
                .set_series_opts(label_opts=options.LabelOpts(is_show=False)) \
                .set_global_opts(title_opts=options.TitleOpts(title="Timeline эмоций"),
                                 xaxis_opts=options.AxisOpts(interval=60)) \
                .reversal_axis()
            for index, row in data.iterrows():
                if i * 1200 < row.cumulative_duration <= (i + 1) * 1200:
                    if self.username == "ALL":
                        text = f"{row.username} - {row.text}"
                    else:
                        text = row.text
                    item = options.BarItem(
                        name=text,
                        value=row.duration
                    )
                else:
                    item = options.BarItem(
                        name=row.text,
                        value=0
                    )
                bar.add_yaxis(self._label_to_emotion[row.emotion], [item], stack="time",
                              label_opts=options.LabelOpts(is_show=False))
            if i + 1 == n_intervals:
                end_minute = round(total_time / 60)
                timeline.add(bar, f"{i * 20} мин. - {end_minute} мин.")
            else:
                timeline.add(bar, f"{i * 20} мин. - {(i + 1) * 20} мин.")

        return timeline

    def _emotion_words_table(self, data):
        emotion_labels = data.emotion.unique()
        emotion_top_words = list(
            map(lambda x: FreqDist(self._preprocess(data[data.emotion == x].text)).most_common(10), emotion_labels))
        headers = list(map(lambda x: self._label_to_emotion[x], emotion_labels))
        rows = list()
        for i in range(0, 10):
            row = list()
            for emotion in emotion_top_words:
                try:
                    row.append(f"{emotion[i][0]} - {emotion[i][1]}")
                except:
                    row.append("")
            rows.append(row)

        table = Table()

        table.add(headers, rows)
        table.set_global_opts(
            title_opts=options.ComponentTitleOpts(title="Частота слов по эмоциям")
        )

        return table

    def _generate_page(self, user_data):
        page = Page(layout=Page.SimplePageLayout, page_title=self.username)
        page.add(
            self._wordcloud(user_data),
            self._emotions_duration_pie(user_data),
            self._emotions_timeline(user_data),
            self._emotion_words_table(user_data)
        )
        page_path = f'temp_voice/{self.guild_id}_{self.username}.html'
        page.render(page_path)

        return page_path


class AllUsersData(UserData):
    def __init__(self, guild_id, data):
        super().__init__("ALL", guild_id, data)

    @staticmethod
    def _user_duration_pie(data):
        data = data.drop(columns=["text", "timestamp", "emotion"])
        data = data.groupby("username")["duration"].sum()
        keys = data.index.tolist()
        values = data.values.tolist()
        values = map(lambda x: round(x), values)

        chart = Pie(init_opts=options.InitOpts(width="50%")) \
            .add("Длительность в секундах",
                 [list(z) for z in zip(keys, values)],
                 radius=["30%", "75%"],
                 rosetype="radius"
                 ) \
            .set_global_opts(title_opts=options.TitleOpts(title="Участие в разговоре"),
                             legend_opts=options.LegendOpts(is_show=False)) \
            .set_series_opts(label_opts=options.LabelOpts(formatter="{b}: {d}%"))

        return chart

    def _user_emotions(self, data):
        data = data.drop(columns=["text", "timestamp"])
        data = data.groupby(["emotion", "username"])["duration"].sum()
        data = data.unstack()
        charts = list()
        for emotion in data.index.tolist():
            emotion_data = data.loc[[emotion]]
            values = emotion_data.iloc[0].to_list()
            keys = emotion_data.columns.to_list()

            chart = Pie(init_opts=options.InitOpts(width="50%")) \
                .add("Длительность в секундах",
                     [list(z) for z in zip(keys, values)],
                     radius=["30%", "75%"],
                     rosetype="radius"
                     ) \
                .set_global_opts(title_opts=options.TitleOpts(title=self._label_to_emotion[emotion]),
                                 legend_opts=options.LegendOpts(is_show=False)) \
                .set_series_opts(label_opts=options.LabelOpts(formatter="{b}: {d}%"))

            charts.append(chart)

        return charts

    def _generate_page(self, user_data):
        page = Page(layout=Page.SimplePageLayout, page_title=self.username)
        page.add(
            self._wordcloud(user_data),
            self._emotions_duration_pie(user_data),
            self._user_duration_pie(user_data),
            *self._user_emotions(user_data),
            self._emotions_timeline(user_data),
            self._emotion_words_table(user_data)
        )
        page_path = f'temp_voice/{self.guild_id}_{self.username}.html'
        page.render(page_path)

        return page_path


def _csv_to_pandas(file_path):
    file = pd.read_csv(file_path, header=None, encoding='windows-1251')
    file.columns = ["timestamp", "duration", "username", "emotion", "text"]

    return file


def visualize_report(file_path, guild_id):
    df = _csv_to_pandas(file_path)
    unique_users = df.username.unique()
    user_obj = list()
    if len(unique_users) > 1:
        user_obj.append(AllUsersData(guild_id, df))
    for user in unique_users:
        user_obj.append(UserData(user, guild_id, df[df.username == user].drop(columns="username")))

    return list(map(lambda x: x.results_page, user_obj))
