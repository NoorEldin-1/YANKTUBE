import { useDispatch, useSelector } from "react-redux";
import { setVideoInfo } from "../store/youtubeSlice";
import {
  Card,
  Image,
  Text,
  Badge,
  Button,
  Group,
  ActionIcon,
} from "@mantine/core";
import { IconDownload, IconBrandYoutubeFilled } from "@tabler/icons-react";
import { setDialog } from "../store/dialogSlice";
import { useCallback } from "react";

const VideoDetails = () => {
  const dispatch = useDispatch();
  const { videoDetails } = useSelector((state) => state.youtube);

  const handleOpenYoutube = useCallback(() => {
    window.open(`https://www.youtube.com/watch?v=${videoDetails.id}`, "_blank");
  }, [videoDetails?.id]);

  const handleDownload = useCallback(() => {
    dispatch(setDialog("DownloadVideoOptions"));
    dispatch(setVideoInfo(videoDetails));
  }, [dispatch, videoDetails]);

  if (!videoDetails) return null;

  return (
    <Card
      shadow="xl"
      padding="xl"
      radius="2xl"
      style={{
        width: "100%",
        background:
          "linear-gradient(135deg, rgba(255,255,255,0.15), rgba(255,255,255,0.05))",
        border: "1px solid rgba(255, 255, 255, 0.25)",
        boxShadow: "0 8px 24px rgba(0, 0, 0, 0.2)",
        transition: "transform 300ms ease, box-shadow 300ms ease",
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = "translateY(-4px)";
        e.currentTarget.style.boxShadow = "0 12px 32px rgba(0,0,0,0.25)";
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = "translateY(0)";
        e.currentTarget.style.boxShadow = "0 8px 24px rgba(0,0,0,0.2)";
      }}
    >
      <Card.Section style={{ overflow: "hidden", borderRadius: "1rem" }}>
        <Image
          src={`https://img.youtube.com/vi/${videoDetails.id}/maxresdefault.jpg`}
          height={220}
          alt={videoDetails.title}
          style={{
            objectFit: "cover",
            transform: "scale(1.02)",
            transition: "transform 400ms ease",
          }}
          onMouseEnter={(e) =>
            (e.currentTarget.style.transform = "scale(1.08)")
          }
          onMouseLeave={(e) =>
            (e.currentTarget.style.transform = "scale(1.02)")
          }
        />
      </Card.Section>

      <Group mt="lg" mb="sm" justify="space-between" align="center">
        <Text fw={600} size="sm" style={{ letterSpacing: "0.6px" }}>
          @{videoDetails.uploader}
        </Text>

        <Group gap="sm">
          <ActionIcon
            onClick={handleOpenYoutube}
            variant="gradient"
            gradient={{ from: "#667eea", to: "#764ba2" }}
            size="lg"
            radius="xl"
            style={{ transition: "transform 200ms ease" }}
            onMouseEnter={(e) =>
              (e.currentTarget.style.transform = "scale(1.1)")
            }
            onMouseLeave={(e) => (e.currentTarget.style.transform = "scale(1)")}
          >
            <IconBrandYoutubeFilled style={{ width: "65%", height: "65%" }} />
          </ActionIcon>

          <Badge
            size="md"
            variant="gradient"
            gradient={{ from: "#667eea", to: "#764ba2" }}
            style={{
              textTransform: "none",
              fontWeight: 600,
              borderRadius: "0.75rem",
              padding: "0.4rem 0.8rem",
            }}
          >
            {`${Math.floor(videoDetails.duration / 60)} min`}
          </Badge>
        </Group>
      </Group>

      <Text size="sm" style={{ lineHeight: 1.6, color: "white" }}>
        {videoDetails.title}
      </Text>

      <Button
        variant="gradient"
        gradient={{ from: "#667eea", to: "#764ba2" }}
        fullWidth
        mt="lg"
        radius="xl"
        rightSection={<IconDownload size={16} />}
        size="lg"
        styles={{
          root: {
            textTransform: "uppercase",
            fontWeight: 700,
            letterSpacing: "1px",
            transition: "all 300ms ease",
          },
        }}
        onMouseEnter={(e) =>
          (e.currentTarget.style.transform = "translateY(-2px)")
        }
        onMouseLeave={(e) =>
          (e.currentTarget.style.transform = "translateY(0)")
        }
        onClick={handleDownload}
      >
        Download
      </Button>
    </Card>
  );
};

export default VideoDetails;
