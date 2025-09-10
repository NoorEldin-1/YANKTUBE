import "./App.css";
import { useSelector } from "react-redux";
import GetDetails from "./components/GetDetails";
import VideoDetails from "./components/VideoDetails";
import PlaylistDetails from "./components/PlaylistDetails";
import "@mantine/core/styles.css";
import { MantineProvider } from "@mantine/core";
import DownloadVideoOptions from "./components/DownloadVideoOptions";
import DownloadPlaylistOptions from "./components/DownloadPlaylistOptions";

function App() {
  const videoDetails = useSelector((state) => state.youtube.videoDetails);
  const playlistDetails = useSelector((state) => state.youtube.playlistDetails);
  const dialog = useSelector((state) => state.dialog);

  return (
    <MantineProvider defaultColorScheme="dark">
      <div
        style={{
          display: "flex",
          justifyContent: "center",
          padding: "40px 20px",
          minHeight: "100vh",
          fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
          background:
            "linear-gradient(135deg, #280067, #77006a, #b5005b, #e4003d, #ff0000)",
        }}
      >
        <div
          style={{
            width: "100%",
            maxWidth: "1400px",
            background: "rgba(255, 255, 255, 0.05)",
            borderRadius: "24px",
            padding: "10px",
            boxShadow: "0 12px 40px rgba(0,0,0,0.35)",
            border: "1px solid rgba(255, 255, 255, 0.15)",
            display: "flex",
            flexDirection: "column",
            alignItems: "stretch",
            gap: "32px",
          }}
        >
          <GetDetails />
          {videoDetails && <VideoDetails />}
          {playlistDetails && <PlaylistDetails />}
        </div>
      </div>

      {dialog === "DownloadVideoOptions" && <DownloadVideoOptions />}
      {dialog === "DownloadPlaylistOptions" && <DownloadPlaylistOptions />}
    </MantineProvider>
  );
}

export default App;
