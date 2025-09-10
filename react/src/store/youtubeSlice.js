import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import { API_BASE } from "../main";
import axios from "axios";

export const getDetails = createAsyncThunk(
  "youtube/getDetails",
  async (url) => {
    if (!url) return;
    const res = await axios.get(`${API_BASE}/details`, {
      params: {
        url: url,
      },
    });
    return res.data;
  }
);

export const downloadSingleVideo = createAsyncThunk(
  "youtube/downloadSingleVideo",
  async ({ url, videoQuality }) => {
    if (!url) return;
    const res = await axios.get(`${API_BASE}/download/video`, {
      params: {
        url: url,
        quality: videoQuality,
      },
      responseType: "blob",
    });
    const contentDisposition = res.headers["content-disposition"];
    let filename = "video.mp4";
    if (contentDisposition) {
      const starMatch = contentDisposition.match(
        /filename\*=([^']*)''([^;\n]+)/i
      );
      if (starMatch && starMatch[2]) {
        let decoded = starMatch[2];
        try {
          decoded = decodeURIComponent(decoded);
        } catch {
          // تجاهل خطأ فك التشفير واستخدام الاسم الأصلي
        }
        filename = decoded;
      } else {
        const simpleMatch = contentDisposition.match(
          /filename\s*=\s*"?([^";\n]+)"?/i
        );
        if (simpleMatch && simpleMatch[1]) {
          filename = simpleMatch[1];
        }
      }
    }
    const blob = new Blob([res.data], {
      type: res.headers["content-type"] || "video/mp4",
    });
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = downloadUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(downloadUrl);
  }
);

export const downloadSingleAudio = createAsyncThunk(
  "youtube/downloadSingleAudio",
  async ({ url }) => {
    if (!url) return;
    const response = await axios.get(`${API_BASE}/download/audio`, {
      params: {
        url: url,
      },
      responseType: "blob",
    });
    const contentDisposition = response.headers["content-disposition"];
    let filename = "audio.mp3";
    if (contentDisposition) {
      const starMatch = contentDisposition.match(
        /filename\*=([^']*)''([^;\n]+)/i
      );
      if (starMatch && starMatch[2]) {
        let decoded = starMatch[2];
        try {
          decoded = decodeURIComponent(decoded);
        } catch {
          // ignore decode error, use raw
        }
        filename = decoded;
      } else {
        const simpleMatch = contentDisposition.match(
          /filename\s*=\s*"?([^";\n]+)"?/i
        );
        if (simpleMatch && simpleMatch[1]) {
          filename = simpleMatch[1];
        }
      }
    }

    const blob = new Blob([response.data], {
      type: response.headers["content-type"] || "audio/mpeg",
    });

    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = downloadUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(downloadUrl);
  }
);

export const downloadPlaylistVideo = createAsyncThunk(
  "youtube/downloadPlaylistVideo",
  async ({ url, quality }) => {
    if (!url || !quality) return;
    const response = await axios.get(`${API_BASE}/download/playlist/video`, {
      params: {
        url: url,
        quality: quality,
      },
      responseType: "blob",
      timeout: 600000,
    });

    const contentDisposition = response.headers["content-disposition"];
    let filename = "playlist_videos.zip";
    if (contentDisposition) {
      const starMatch = contentDisposition.match(
        /filename\*=([^']*)''([^;\n]+)/i
      );
      if (starMatch && starMatch[2]) {
        let decoded = starMatch[2];
        try {
          decoded = decodeURIComponent(decoded);
        } catch {
          // ignore decode error, use raw
        }
        filename = decoded;
      } else {
        const simpleMatch = contentDisposition.match(
          /filename\s*=\s*"?([^";\n]+)"?/i
        );
        if (simpleMatch && simpleMatch[1]) {
          filename = simpleMatch[1];
        }
      }
    }

    const blob = new Blob([response.data], {
      type: response.headers["content-type"] || "application/zip",
    });

    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = downloadUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(downloadUrl);
  }
);

export const downloadPlaylistAudio = createAsyncThunk(
  "youtube/downloadPlaylistAudio",
  async ({ url }) => {
    if (!url) return;

    const response = await axios.get(`${API_BASE}/download/playlist/audio`, {
      params: {
        url: url,
      },
      responseType: "blob",
      timeout: 600000,
    });

    const contentDisposition = response.headers["content-disposition"];
    let filename = "playlist_audio.zip";
    if (contentDisposition) {
      const starMatch = contentDisposition.match(
        /filename\*=([^']*)''([^;\n]+)/i
      );
      if (starMatch && starMatch[2]) {
        let decoded = starMatch[2];
        try {
          decoded = decodeURIComponent(decoded);
        } catch {
          // ignore decode error, use raw
        }
        filename = decoded;
      } else {
        const simpleMatch = contentDisposition.match(
          /filename\s*=\s*"?([^";\n]+)"?/i
        );
        if (simpleMatch && simpleMatch[1]) {
          filename = simpleMatch[1];
        }
      }
    }

    const blob = new Blob([response.data], {
      type: response.headers["content-type"] || "application/zip",
    });

    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = downloadUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(downloadUrl);
  }
);

const youtubeSlice = createSlice({
  name: "youtube",
  initialState: {
    url: "",
    getDetailsLoading: false,
    videoDetails: null,
    playlistDetails: null,
    downloadSingleVideoLoading: false,
    downloadSingleAudioLoading: false,
    downloadPlaylistVideoLoading: false,
    downloadPlaylistAudioLoading: false,
    VideoInfo: null,
    PlaylistInfo: null,
  },
  reducers: {
    setVideoInfo: (state, action) => {
      state.VideoInfo = action.payload;
    },
    setPlaylistInfo: (state, action) => {
      state.PlaylistInfo = action.payload;
    },
    setUrl: (state, action) => {
      state.url = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(getDetails.pending, (state) => {
        state.videoDetails = null;
        state.playlistDetails = null;
        state.getDetailsLoading = true;
      })
      .addCase(getDetails.fulfilled, (state, action) => {
        state.getDetailsLoading = false;
        if (action.payload.type === "video") {
          state.videoDetails = action.payload;
        } else if (action.payload.type === "playlist") {
          state.playlistDetails = action.payload;
        }
      })
      .addCase(downloadSingleVideo.pending, (state) => {
        state.downloadSingleVideoLoading = true;
      })
      .addCase(downloadSingleVideo.fulfilled, (state) => {
        state.downloadSingleVideoLoading = false;
      })
      .addCase(downloadSingleAudio.pending, (state) => {
        state.downloadSingleAudioLoading = true;
      })
      .addCase(downloadSingleAudio.fulfilled, (state) => {
        state.downloadSingleAudioLoading = false;
      })
      .addCase(downloadPlaylistVideo.pending, (state) => {
        state.downloadPlaylistVideoLoading = true;
      })
      .addCase(downloadPlaylistVideo.fulfilled, (state) => {
        state.downloadPlaylistVideoLoading = false;
      })
      .addCase(downloadPlaylistAudio.pending, (state) => {
        state.downloadPlaylistAudioLoading = true;
      })
      .addCase(downloadPlaylistAudio.fulfilled, (state) => {
        state.downloadPlaylistAudioLoading = false;
      });
  },
});

export const { setVideoInfo, setPlaylistInfo, setUrl } = youtubeSlice.actions;
export default youtubeSlice.reducer;
