import os
from datetime import datetime

from discord.sinks.core import Filters, Sink, default_filters
from pydub import AudioSegment
from pydub.silence import detect_nonsilent


class StreamSink(Sink):
    def __init__(self, guild_id, *, filters=None):
        if filters is None:
            filters = default_filters
        self.filters = filters
        Filters.__init__(self, **self.filters)
        self.vc = None
        self.recorded_users = []
        self.guild_id = guild_id

        self.buffer = StreamBuffer(guild_id)
        self.buffer.create_folder()

    def write(self, data, user):
        if user not in self.recorded_users:
            self.recorded_users.append(user)
            self.buffer.byte_buffer[user] = bytearray()

        self.buffer.write(data=data, user=user)

    def cleanup(self):
        self.finished = True

    def get_all_audio(self):
        pass

    def get_user_audio(self, user):
        pass


class StreamBuffer:
    def __init__(self, guild_id) -> None:
        self.guild_id = guild_id
        self.sample_width = 2
        self.channels = 2
        self.sample_rate = 48000
        self.bytes_ps = self.sample_rate * self.channels * self.sample_width
        self.min_rec_len = 0.3
        self.min_rec_size = self.bytes_ps * self.min_rec_len
        self.byte_buffer = {}

    def write(self, data, user):
        self.byte_buffer[user] += data
        if len(data) > self.min_rec_size:
            audio_segment = AudioSegment(data=self.byte_buffer[user],
                                         sample_width=self.sample_width,
                                         frame_rate=self.sample_rate,
                                         channels=self.channels)

            self.byte_buffer[user] = bytearray()

            non_silent = detect_nonsilent(audio_segment, silence_thresh=audio_segment.dBFS - 16, seek_step=10)
            for interval in non_silent:
                start_time = interval[0]
                if interval[1] + 100 > len(audio_segment):
                    end_time = len(audio_segment)
                else:
                    end_time = interval[1] + 100

                audio_segment[start_time:end_time].export(f"temp_voice/{self.guild_id}/"
                                                          f"{user}_{datetime.now().strftime('%Y%m%d%H%M%S')}.wav",
                                                          format="wav")

    def create_folder(self):
        if not os.path.exists(f"temp_voice/{self.guild_id}"):
            os.makedirs(f"temp_voice/{self.guild_id}")
