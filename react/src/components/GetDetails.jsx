import React, { useMemo } from "react";
import { useDispatch, useSelector } from "react-redux";
import { getDetails, setUrl } from "../store/youtubeSlice";
import { ActionIcon, Input } from "@mantine/core";
import { IconFileDescription } from "@tabler/icons-react";

const GetDetails = () => {
  const dispatch = useDispatch();
  const { getDetailsLoading, url } = useSelector((state) => state.youtube);

  const inputElement = useMemo(() => {
    return (
      <Input
        value={url}
        onChange={(e) => dispatch(setUrl(e.target.value))}
        type="text"
        placeholder="Enter YouTube URL"
        radius="xl"
        size="md"
        variant="filled"
        style={{
          flexGrow: 1,
          boxShadow: "0 4px 12px rgba(0,0,0,0.15)",
          transition: "all 200ms ease",
        }}
        styles={{
          input: {
            color: "white",
            background: "rgba(255,255,255,0.08)",
            border: "1px solid rgba(255,255,255,0.25)",
            transition: "border-color 200ms ease, box-shadow 200ms ease",
          },
        }}
        onFocus={(e) => {
          e.currentTarget.style.borderColor = "#77006a";
          e.currentTarget.style.boxShadow = "0 0 0 3px rgba(119,0,106,0.4)";
        }}
        onBlur={(e) => {
          e.currentTarget.style.borderColor = "rgba(255,255,255,0.25)";
          e.currentTarget.style.boxShadow = "none";
        }}
      />
    );
  }, [dispatch, url]);

  const actionElement = useMemo(() => {
    return (
      <ActionIcon
        onClick={() => {
          if (!url) return;
          dispatch(getDetails(url));
        }}
        variant="gradient"
        gradient={{ from: "#280067", to: "#77006a", deg: 45 }}
        loading={getDetailsLoading}
        loaderProps={{ type: "dots" }}
        size="xl"
        radius="xl"
      >
        <IconFileDescription style={{ width: "65%", height: "65%" }} />
      </ActionIcon>
    );
  }, [dispatch, getDetailsLoading, url]);

  const element = useMemo(() => {
    return (
      <div
        style={{
          display: "flex",
          gap: "10px",
          alignItems: "center",
          width: "100%",
          marginBottom: "24px",
        }}
      >
        {inputElement}
        {actionElement}
      </div>
    );
  }, [actionElement, inputElement]);

  return element;
};

export default GetDetails;
