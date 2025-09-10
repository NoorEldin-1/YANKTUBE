import { Button, Flex, Modal, Text, LoadingOverlay } from "@mantine/core";
import { useDispatch, useSelector } from "react-redux";
import { setDialog } from "../store/dialogSlice";
import { IconVideo, IconMusic } from "@tabler/icons-react";
import {
  downloadPlaylistAudio,
  downloadPlaylistVideo,
} from "../store/youtubeSlice";

const options = [
  { text: "quality 1080p", value: "1080p" },
  { text: "quality 720p", value: "720p" },
  { text: "quality 480p", value: "480p" },
  { text: "quality 360p", value: "360p" },
  { text: "quality 240p", value: "240p" },
  { text: "quality 144p", value: "144p" },
];

// 🎨 زر موحد
const GradientButton = ({ children, icon, onClick }) => (
  <Button
    leftSection={icon}
    variant="gradient"
    gradient={{ from: "#280067", to: "#77006a", deg: 45 }}
    fullWidth
    size="lg"
    radius="xl"
    styles={{
      root: {
        textTransform: "uppercase",
        fontWeight: 600,
        letterSpacing: "0.5px",
        transition: "all 250ms ease",
      },
    }}
    onMouseEnter={(e) => (e.currentTarget.style.transform = "translateY(-2px)")}
    onMouseLeave={(e) => (e.currentTarget.style.transform = "translateY(0)")}
    onClick={onClick}
  >
    {children}
  </Button>
);

const DownloadPlaylistOptions = () => {
  const dispatch = useDispatch();
  const dialog = useSelector((state) => state.dialog);
  const playlistInfo = useSelector((state) => state.youtube.PlaylistInfo);

  const videoLoading = useSelector(
    (state) => state.youtube.downloadPlaylistVideoLoading
  );
  const audioLoading = useSelector(
    (state) => state.youtube.downloadPlaylistAudioLoading
  );

  const isLoading = videoLoading || audioLoading;

  return (
    <>
      <Modal
        opened={dialog === "DownloadPlaylistOptions"}
        withCloseButton
        closeOnClickOutside={false}
        onClose={() => dispatch(setDialog(""))}
        title={
          <Text
            fw={700}
            size="lg"
            style={{
              textTransform: "uppercase",
              letterSpacing: "1px",
              background: "linear-gradient(90deg, #280067, #77006a)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
            }}
          >
            Playlist Options
          </Text>
        }
        size="xl"
        radius="lg"
        overlayProps={{ blur: 6, backgroundOpacity: 0.55 }}
        transitionProps={{ transition: "pop", duration: 250 }}
        styles={{
          content: {
            borderRadius: "1.5rem",
            background:
              "linear-gradient(135deg, rgba(255,255,255,0.12), rgba(255,255,255,0.06))",
            border: "1px solid rgba(255,255,255,0.2)",
          },
          close: {
            width: "40px",
            height: "40px",
            borderRadius: "50%",
            transition: "transform 200ms ease",
          },
          header: { marginBottom: "1rem" },
        }}
      >
        <Flex direction="column" gap="md" justify="center" align="stretch">
          {options.map((option) => (
            <GradientButton
              key={option.value}
              icon={<IconVideo />}
              onClick={() =>
                dispatch(
                  downloadPlaylistVideo({
                    url: `https://www.youtube.com/playlist?list=${playlistInfo.playlist_id}`,
                    quality: option.value,
                  })
                )
              }
            >
              {option.text}
            </GradientButton>
          ))}

          <GradientButton
            icon={<IconMusic />}
            onClick={() =>
              dispatch(
                downloadPlaylistAudio({
                  url: `https://www.youtube.com/playlist?list=${playlistInfo.playlist_id}`,
                })
              )
            }
          >
            audio mp3
          </GradientButton>
        </Flex>
      </Modal>

      <LoadingOverlay
        styles={{
          root: { position: "fixed" },
          loader: { transform: "scale(1.2)" },
        }}
        visible={isLoading}
        zIndex={1000}
        overlayProps={{ radius: "md", blur: 3 }}
        loaderProps={{ type: "bars", color: "#77006a", size: "lg" }}
      />
    </>
  );
};

export default DownloadPlaylistOptions;
