import { createSlice } from "@reduxjs/toolkit";

const dialogSlice = createSlice({
  name: "dialog",
  initialState: "",
  reducers: {
    setDialog: (state, action) => {
      return (state = action.payload);
    },
  },
});

export const { setDialog } = dialogSlice.actions;
export default dialogSlice.reducer;
