import { Config } from "@remotion/cli/config";
import { enableTailwind } from '@remotion/tailwind-v4';

Config.setVideoImageFormat("jpeg");
Config.setOverwriteOutput(true);

Config.overrideWebpackConfig((currentConfig) => {
  const tailwindConfig = enableTailwind(currentConfig);
  return {
    ...tailwindConfig,
    output: {
      ...tailwindConfig.output,
      hashFunction: "xxhash64",  // algorithme compatible Node.js v24
    },
  };
});