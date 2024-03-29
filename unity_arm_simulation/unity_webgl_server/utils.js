window.gameInstance = null;

const main = () => {

    window.addEventListener("resize", function () {
        var canvas = document.getElementById("unity-canvas");
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    });

    window.gameInstance = createUnityInstance(
      
        document.querySelector("#unity-canvas"),
        {
            dataUrl: "webgl_build/Build/webgl_build.data.gz",
            frameworkUrl: "webgl_build/Build/webgl_build.framework.js.gz",
            codeUrl: "webgl_build/Build/webgl_build.wasm.gz",
            streamingAssetsUrl: "StreamingAssets",
            companyName: "DefaultCompany",
            productName: "arm_sim",
            productVersion: "0.1",
            matchWebGLToCanvasSize: false,
        }
    );

   if (!window.console) window.console = {};
            const noop = () => {};
            console.log = noop;
            console.error = noop;
            console.warn = noop;
            console.info = noop;
            console.debug = noop;

    };
main();
