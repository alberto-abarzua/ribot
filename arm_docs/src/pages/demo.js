import useDocusaurusContext from "@docusaurus/useDocusaurusContext";
import Layout from "@theme/Layout";
// import GeneralGif from "@site/static/img/general_page.gif";
import ActivityBox from "@site/static/img/activity_box.png";
import Euler from "@site/static/img/euler.gif";
import Coordinates from "@site/static/img/coordinates.gif";
import ArrowDownSVG from "@site/static/img/down_arrow.svg";

// <img
//   src={GeneralGif}
//   alt="General Overview"
//   className="w-1/3 flex-shrink-0 overflow-hidden rounded-md object-contain"
// />
export default function Home() {
  const { siteConfig } = useDocusaurusContext();
  const onClickGoToActivity = () => {
    const url =
      "https://demo.ribot.dev/?access_token=QslklxkIoFrDMqjQPwSIaFabSlBnOUTzxRMlVgxuSUWhRijUvsNZWjDxyXwnhaFE";
    // go to url in new tab
    window.open(url, "_blank");
  };
  return (
    <Layout
      title={`Hello from ${siteConfig.title}`}
      description="Description will go into a meta tag in <head />"
    >
      <main className="flex flex-col justify-center p-10 ">
        <div className="flex flex-col">
          <h1 className="text-3xl font-bold mb-2">
            Prueba de Usabilidad - Plataforma de Control Brazo Robótico
          </h1>
          <div className="bg-slate-100 w-fit text-gray-800 rounded-full px-4 py-1">
            <span className="px-2 text-lg font-bold">Duración Estimada:</span>
            <span>15 Minutos</span>
          </div>

          <div className="flex justify-center">
            <div>
              <div className="flex flex-col mt-5">
                <p className="text-lg flex-1 px-2 py-3">
                  ¡Hola! Muchas gracias por querer ayudarme con mi trabajo de
                  título. Esta es una pequeña actividad interactiva con la
                  página que he estado construyendo este semestre. La idea es
                  que puedas probar la página para ver si es fácil de usar y si
                  es intuitiva.
                </p>
                <h3 className="text-2xl font-bold">
                  ¿Qué se necesita antes de hacerla?
                </h3>

                <ul class="list-disc pl-5">
                  <li class="text-lg mx-2">Leer este documento</li>
                  <li class="text-lg  mx-2">Un poco de inglés</li>
                  <li class="text-lg  mx-2">
                    Un computador/laptop (No se puede hacer en dispositivos
                    móviles)
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <div className="flex flex-col mt-10">
          <h3 className="text-2xl font-bold">
            ¿Cómo se mueve un brazo robótico?
          </h3>
          <p className="text-lg flex-1 px-2 py-3">
            Un brazo robótico se mueve a través de articulaciones y motores que
            replican de alguna manera la movilidad y funcionalidad del brazo
            humano. Estos movimientos se controlan mediante un software que
            permite la precisión en tareas específicas.
          </p>

          <div className="flex justify-center gap-x-6">
            <div className="flex flex-col flex-1 items-center">
              <p className="text-xl font-bold flex-1 px-2 py-3">Coordenadas</p>
              <div className="flex ">
                <p className="text-lg flex-1 px-2 py-3">
                  Las coordenadas son un conjunto de valores que determinan la
                  posición exacta de un punto en un espacio. En robótica, se
                  utilizan para dirigir el movimiento del brazo en tres
                  dimensiones: X, Y y Z.
                </p>
                <img
                  src={Coordinates}
                  alt="Coordinates Explanation"
                  className="w-64 flex-shrink-0 overflow-hidden rounded-md object-contain"
                />
              </div>
            </div>
            <div className="flex flex-col flex-1 items-center">
              <p className="text-xl font-bold flex-1 px-2 py-3">
                Ángulos de Aproximación
              </p>
              <div className="flex ">
                <p className="text-lg flex-1 px-2 py-3">
                  Los ángulos de aproximación, como el roll, pitch y yaw, se
                  refieren a las rotaciones en torno a los ejes principales del
                  brazo robótico. Estos ángulos son fundamentales para la
                  orientación y el posicionamiento preciso del extremo del
                  brazo.
                </p>
                <img
                  src={Euler}
                  alt="Angles of Approach Explanation"
                  className="w-64 flex-shrink-0 overflow-hidden rounded-md object-contain"
                />
              </div>
            </div>
          </div>
        </div>

        <div className="flex flex-col mt-10">
          <h3 className="text-2xl font-bold">La Actividad!</h3>
          <div className="flex items-center justify-center gap-x-20 ">
            <div className="flex">
              <p className="text-lg flex-1 px-2 py-3">
                Veras un recuadro como el de la imagen de la derecha. Este
                recuadro te dira que hacer en cada paso. Sigue las instrucciones
                y completa la actividad. Al final se abrirá un formulario para
                que puedas dejar tus comentarios sobre la actividad. (Es
                importante que completes el formulario para que la actividad sea
                válida)
              </p>

              <img
                src={ActivityBox}
                alt="Angles of Approach Explanation"
                className="w-1/4 flex-shrink-0 overflow-hidden rounded-md object-contain"
              />
            </div>
          </div>
          <ArrowDownSVG className="w-10 h-10 mx-auto mt-5 transform scale-50 transition-all animate-bounce" />
          <div className="flex justify-center mt-5">
            <button
              onClick={onClickGoToActivity}
              className="bg-green-600 text-white  transform scale-150 px-4 py-2 rounded-md hover:bg-green-700 font-mono"
            >
              Comenzar la Actividad
            </button>
          </div>
        </div>
      </main>
    </Layout>
  );
}