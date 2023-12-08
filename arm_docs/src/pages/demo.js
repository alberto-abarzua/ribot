import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import ActivityBox from '@site/static/img/activity_box.png';
import Euler from '@site/static/img/euler.gif';
import Coordinates from '@site/static/img/coordinates.gif';
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
                        <span className="px-2 text-lg font-bold">duración estimada:</span>
                        <span>15 minutos</span>
                    </div>

                    <div className="m-auto flex h-1/2 w-1/2 flex-col items-center justify-center rounded-md border border-gray-800 bg-orange-100 p-10 font-mono shadow-sm">
                        <h1 className="mb-2 text-2xl font-bold">La Actividad a Finalizado</h1>
                    </div>
                </div>
            </main>
        </Layout>
    );
}
