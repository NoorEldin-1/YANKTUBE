import { configureStore } from "@reduxjs/toolkit";
import youtubeReducer from "./youtubeSlice";
import dialogReducer from "./dialogSlice";

export const store = configureStore({
  reducer: {
    youtube: youtubeReducer,
    dialog: dialogReducer,
  },
});
