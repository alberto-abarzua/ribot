import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
// import GeneralGif from "@site/static/img/general_page.gif";
import ActivityBox from '@site/static/img/activity_box.png';
import Euler from '@site/static/img/euler.gif';
import Coordinates from '@site/static/img/coordinates.gif';
import ArrowDownSVG from '@site/static/img/down_arrow.svg';
import { useLocation } from 'react-router-dom';

export default function Home() {
    const { siteConfig } = useDocusaurusContext();
    const location = useLocation();
    const searchParams = new URLSearchParams(location.search);
    const token = searchParams.get('access_token');
    const onClickGoToActivity = () => {
        const url = `https://demo.ribot.dev/?access_token=${token}&activity=true`;
        window.open(url, '_blank');
    };
    return (
        <Layout
            title={`Demo - ${siteConfig.title}`}
            description="Demo Page for Ribot Control Software"
        >
            <main className="mx-auto flex w-full flex-col justify-center p-10 lg:w-4/5 ">
                <div className="flex flex-col">
                    <h1 className="mb-2 text-3xl font-bold">
                        Prueba de Usabilidad - Plataforma de Control Brazo Robótico
                    </h1>
                    <div className="w-fit rounded-full bg-slate-100 px-4 py-1 text-gray-800">
                        <span className="px-2 text-lg font-bold">Duración Estimada:</span>
                        <span>15 Minutos</span>
                    </div>

                    <div className="flex justify-center">
                        <div>
                            <div className="mt-5 flex flex-col">
                                <p className="flex-1 px-2 py-3 text-lg">
                                    ¡Hola! Muchas gracias por querer ayudarme con mi trabajo de
                                    título. Esta es una pequeña actividad interactiva con la página
                                    que he estado construyendo este semestre. La idea es que puedas
                                    probar la página para ver si es fácil de usar y si es intuitiva.
                                </p>
                                <h3 className="text-2xl font-bold">
                                    ¿Qué se necesita antes de hacerla?
                                </h3>

                                <ul class="list-disc pl-5">
                                    <li class="mx-2 text-lg">Leer este documento</li>
                                    <li class="mx-2  text-lg">Un poco de inglés</li>
                                    <li class="mx-2  text-lg">
                                        Un computador/laptop (No se puede hacer en dispositivos
                                        móviles)
                                    </li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="mt-10 flex flex-col">
                    <h3 className="text-2xl font-bold">¿Cómo se mueve un brazo robótico?</h3>
                    <p className="flex-1 px-2 py-3 text-lg">
                        Un brazo robótico se mueve a través de articulaciones y motores que replican
                        de alguna manera la movilidad y funcionalidad del brazo humano. Estos
                        movimientos se controlan mediante un software que permite la precisión en
                        tareas específicas.
                    </p>

                    <div className="flex flex-col items-start justify-center gap-x-6 xl:flex-row">
                        <div className="flex w-2/3 flex-1 flex-col ">
                            <p className="flex-1 px-2 py-3 text-xl font-bold">Coordenadas</p>
                            <div className="flex flex-col items-center ">
                                <p className="flex-1 px-2 py-3 text-lg">
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
                        <div className="flex w-2/3 flex-1  flex-col">
                            <p className="flex-1 px-2 py-3 text-xl font-bold">
                                Ángulos de Aproximación
                            </p>
                            <div className="flex flex-col items-center">
                                <p className="flex-1 px-2 py-3 text-lg">
                                    Los ángulos de aproximación, como el roll, pitch y yaw, se
                                    refieren a las rotaciones en torno a los ejes principales del
                                    brazo robótico. Estos ángulos son fundamentales para la
                                    orientación y el posicionamiento preciso del extremo del brazo.
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

                <div className="mt-10 flex flex-col">
                    <h3 className="text-2xl font-bold">La Actividad!</h3>
                    <div className="flex items-start justify-start gap-x-20 ">
                        <div className="flex flex-col lg:flex-row">
                            <div>
                                <p className="flex-1 px-2 py-3 text-lg">
                                    El objetivo de esta actividad sera guiarte a través de la
                                    plataforma para que puedas mover el brazo robótico de manera
                                    libre y generar bloques de acciones para 'programar' el brazo y
                                    que este realice una tarea.
                                </p>

                                <p className="flex-1 px-2 py-3 text-lg">
                                    Veras un recuadro morado como el de la imagen de la derecha.
                                    Este recuadro te dira que hacer en cada paso. Sigue las
                                    instrucciones y completa la actividad. Al final se abrirá un
                                    formulario para que puedas dejar tus comentarios sobre la
                                    actividad. (Es importante que completes el formulario para que
                                    la actividad sea válida)
                                </p>
                            </div>

                            <img
                                src={ActivityBox}
                                alt="Angles of Approach Explanation"
                                className=" mt-5 w-60 flex-shrink-0 rounded-md object-contain object-top"
                            />
                        </div>
                    </div>

                    <div className="mt-16 flex justify-center">
                        <button
                            onClick={onClickGoToActivity}
                            className="scale-150 transform rounded-md  border border-gray-500 bg-green-600 px-4 py-2 font-mono text-white shadow-sm shadow-gray-500 hover:bg-green-700"
                        >
                            Comenzar la Actividad
                        </button>
                    </div>
                </div>
            </main>
        </Layout>
    );
}
