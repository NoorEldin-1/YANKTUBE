import { useDispatch, useSelector } from "react-redux";
import { setPlaylistInfo, setVideoInfo } from "../store/youtubeSlice";
import {
  ActionIcon,
  Badge,
  Button,
  Card,
  Group,
  Image,
  Text,
  Flex,
} from "@mantine/core";
import { setDialog } from "../store/dialogSlice";
import { IconDownload, IconBrandYoutubeFilled } from "@tabler/icons-react";
import React from "react";

const PlaylistDetails = () => {
  const dispatch = useDispatch();
  const playlistDetails = useSelector((state) => state.youtube.playlistDetails);

  if (!playlistDetails) return null;

  return (
    <Flex
      direction="column"
      gap="xl"
      justify="center"
      align="center"
      style={{ width: "100%" }}
    >
      <Card
        shadow="xl"
        padding="lg"
        radius="2xl"
        style={{
          width: "100%",
          maxWidth: "700px",
          background:
            "linear-gradient(135deg, rgba(255,255,255,0.15), rgba(255,255,255,0.05))",
          border: "1px solid rgba(255, 255, 255, 0.25)",
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
            src={`https://img.youtube.com/vi/${playlistDetails.videos[0].id}/maxresdefault.jpg`}
            height={200}
            alt="Playlist Thumbnail"
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

        <Group mt="md" mb="xs" justify="space-between" align="center">
          <Text fw={600} size="sm">
            @{playlistDetails.videos[0].uploader}
          </Text>

          <Group gap="sm">
            <ActionIcon
              onClick={() =>
                window.open(
                  `https://www.youtube.com/playlist?list=${playlistDetails.playlist_id}`,
                  "_blank"
                )
              }
              variant="gradient"
              gradient={{ from: "#280067", to: "#77006a", deg: 45 }}
              size="lg"
              radius="xl"
              style={{ transition: "transform 200ms ease" }}
              onMouseEnter={(e) =>
                (e.currentTarget.style.transform = "scale(1.1)")
              }
              onMouseLeave={(e) =>
                (e.currentTarget.style.transform = "scale(1)")
              }
            >
              <IconBrandYoutubeFilled style={{ width: "65%", height: "65%" }} />
            </ActionIcon>

            <Badge
              size="lg"
              variant="gradient"
              gradient={{ from: "#280067", to: "#77006a", deg: 45 }}
              style={{
                borderRadius: "0.75rem",
                padding: "0.4rem 0.8rem",
                fontWeight: 600,
              }}
            >
              {`${playlistDetails.videos.length} videos`}
            </Badge>
          </Group>
        </Group>

        <Text size="lg" fw={600} style={{ lineHeight: 1.4 }}>
          {playlistDetails.playlist_name}
        </Text>

        <Button
          variant="gradient"
          gradient={{ from: "#280067", to: "#77006a", deg: 45 }}
          fullWidth
          mt="md"
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
          onClick={() => {
            dispatch(setDialog("DownloadPlaylistOptions"));
            dispatch(setPlaylistInfo(playlistDetails));
          }}
        >
          Download
        </Button>
      </Card>

      <Flex
        gap="lg"
        justify="center"
        align="flex-start"
        wrap="wrap"
        style={{ width: "100%" }}
      >
        {playlistDetails.videos.map((video) => (
          <SingleVideoCard
            key={video.id}
            video={video}
            onDownload={() => {
              dispatch(setDialog("DownloadVideoOptions"));
              dispatch(setVideoInfo(video));
            }}
          />
        ))}
      </Flex>
    </Flex>
  );
};

const SingleVideoCard = React.memo(({ video, onDownload }) => {
  return (
    <Card
      shadow="md"
      padding="lg"
      radius="xl"
      style={{
        width: "300px",
        background:
          "linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05))",
        border: "1px solid rgba(255, 255, 255, 0.2)",
        transition: "transform 250ms ease, box-shadow 250ms ease",
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = "translateY(-4px)";
        e.currentTarget.style.boxShadow = "0 10px 28px rgba(0,0,0,0.2)";
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = "translateY(0)";
        e.currentTarget.style.boxShadow = "0 6px 18px rgba(0,0,0,0.15)";
      }}
    >
      <Card.Section style={{ overflow: "hidden", borderRadius: "0.75rem" }}>
        <Image
          src={`https://img.youtube.com/vi/${video.id}/maxresdefault.jpg`}
          height={160}
          alt={video.title}
          style={{
            objectFit: "cover",
            transform: "scale(1.02)",
            transition: "transform 350ms ease",
          }}
          onMouseEnter={(e) =>
            (e.currentTarget.style.transform = "scale(1.07)")
          }
          onMouseLeave={(e) =>
            (e.currentTarget.style.transform = "scale(1.02)")
          }
        />
      </Card.Section>

      <Group mt="md" mb="xs" justify="space-between" align="center">
        <Text fw={600} size="xs">
          @{video.uploader}
        </Text>

        <Group gap="sm">
          <ActionIcon
            onClick={() =>
              window.open(
                `https://www.youtube.com/watch?v=${video.id}`,
                "_blank"
              )
            }
            variant="gradient"
            gradient={{ from: "#280067", to: "#77006a", deg: 45 }}
            size="md"
            radius="xl"
            style={{ transition: "transform 200ms ease" }}
            onMouseEnter={(e) =>
              (e.currentTarget.style.transform = "scale(1.1)")
            }
            onMouseLeave={(e) => (e.currentTarget.style.transform = "scale(1)")}
          >
            <IconBrandYoutubeFilled style={{ width: "70%", height: "70%" }} />
          </ActionIcon>

          <Badge
            size="md"
            variant="gradient"
            gradient={{ from: "#280067", to: "#77006a", deg: 45 }}
            style={{
              borderRadius: "0.75rem",
              padding: "0.3rem 0.7rem",
              fontWeight: 600,
            }}
          >
            {`${Math.floor(video.duration / 60)} min`}
          </Badge>
        </Group>
      </Group>

      <Text size="sm" style={{ lineHeight: 1.4, color: "white" }}>
        {video.title}
      </Text>

      <Button
        variant="gradient"
        gradient={{ from: "#280067", to: "#77006a", deg: 45 }}
        fullWidth
        mt="md"
        radius="xl"
        rightSection={<IconDownload size={16} />}
        size="md"
        styles={{
          root: {
            textTransform: "uppercase",
            fontWeight: 700,
            letterSpacing: "0.8px",
            transition: "all 300ms ease",
          },
        }}
        onMouseEnter={(e) =>
          (e.currentTarget.style.transform = "translateY(-2px)")
        }
        onMouseLeave={(e) =>
          (e.currentTarget.style.transform = "translateY(0)")
        }
        onClick={onDownload}
      >
        Download
      </Button>
    </Card>
  );
});

export default PlaylistDetails;
