import React from "react";
import "./index.css";
import { Composition } from "remotion";
import { LessonVideo } from "./LessonVideo";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="LessonVideo"
        component={LessonVideo}
        durationInFrames={18000}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{}}
      />
    </>
  );
};