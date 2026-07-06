import { registerRoot, Composition } from 'remotion'
import { LessonVideo } from './LessonVideo'

export const RemotionRoot = () => {
  return (
    <Composition
      id="LessonVideo"
      component={LessonVideo}
      durationInFrames={1800}
      fps={30}
      width={1920}
      height={1080}
      defaultProps={{
        audioUrl: "",
        segments: [],
        titre: "",
        matiere: "",
        niveau: ""
      }}
    />
  )
}

registerRoot(RemotionRoot)