import os
from datetime import datetime, timedelta
from threading import Timer

from discord.sinks.core import Filters, Sink, default_filters
from pydub import AudioSegment

from pydub.silence import detect_silence


class StreamSink(Sink):
    def __init__(self, guild_id, *, filters=None):
        if filters is None:
            filters = default_filters
        self.filters = filters
        Filters.__init__(self, **self.filters)
        self.vc = None
        self.audio_data = {}
        self.recorded_users = []
        self.guild_id = guild_id
        self.buffer = StreamBuffer(guild_id)
        self.buffer.create_folder()
        self.timer = Timer(5, self.check_write_interval)

    def write(self, data, user):
        self.timer.cancel()
        self.timer = Timer(5, self.check_write_interval)
        if user not in self.recorded_users:
            self.recorded_users.append(user)
            self.buffer.audio_segment[user] = AudioSegment.empty()
            self.buffer.last_write_time[user] = datetime.now()

        self.buffer.write(data=data, user=user)
        self.timer.start()

    def cleanup(self):
        self.finished = True

    def get_all_audio(self):
        pass

    def get_user_audio(self, user):
        pass

    def check_write_interval(self):
        for user in self.buffer.last_write_time:
            if len(self.buffer.audio_segment[user]) != 0 and datetime.now() > self.buffer.last_write_time[user] + \
                    timedelta(seconds=self.buffer.block_len):
                self.buffer.flush_audio(user)


class StreamBuffer:
    def __init__(self, guild_id) -> None:
        self.guild_id = guild_id
        self.byte_buffer = bytearray()
        self.audio_segment = {}
        self.last_write_time = {}

        self.sample_width = 2
        self.channels = 2
        self.sample_rate = 48000
        self.bytes_ps = self.sample_rate * self.channels * self.sample_width
        self.block_len = 1
        self.buff_lim = self.bytes_ps * self.block_len

    def write(self, data, user):
        self.byte_buffer += data

        if len(self.byte_buffer) > self.buff_lim:
            byte_slice = self.byte_buffer[:self.buff_lim]

            temp_audio_segment = AudioSegment(data=byte_slice,
                                              sample_width=self.sample_width,
                                              frame_rate=self.sample_rate,
                                              channels=self.channels)

            silence = detect_silence(temp_audio_segment, silence_thresh=temp_audio_segment.dBFS - 16)

            if len(silence) == 0:
                self.audio_segment[user] += temp_audio_segment
            else:
                if len(self.audio_segment[user]) > 1000:
                    self.flush_audio(user)

            self.byte_buffer = self.byte_buffer[self.buff_lim:]
            self.last_write_time[user] = datetime.now()

    def create_folder(self):
        if not os.path.exists(f"temp_voice/{self.guild_id}"):
            os.makedirs(f"temp_voice/{self.guild_id}")

    def flush_audio(self, user):
        if len(self.audio_segment[user]) != 0:
            silence = detect_silence(self.audio_segment[user], min_silence_len=100,
                                     silence_thresh=self.audio_segment[user].dBFS - 16)
            audio_len = len(self.audio_segment[user])
            silence_len = 0
            for s in silence:
                silence_len += s[1] - s[0]
            if silence_len / audio_len < 0.8:
                self.audio_segment[user].export(f"temp_voice/{self.guild_id}/"
                                                f"{user}_{datetime.now().strftime('%Y%m%d%H%M%S')}.wav", format="wav")
                self.audio_segment[user] = AudioSegment.empty()
