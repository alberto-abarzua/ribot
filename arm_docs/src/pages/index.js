import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import Head from '@docusaurus/Head';
import Link from '@docusaurus/Link';
import HomepageFeatures from '@site/src/components/HomepageFeatures';
import GeneralGif from '@site/static/img/general_page.gif';
import CodeBlock from '@theme/CodeBlock';
function HomepageHeader() {
    const { siteConfig } = useDocusaurusContext();
    return (
        <header className="h-72 w-full bg-orange-400 bg-opacity-90 px-4 py-6">
            <div className="flex h-full w-full flex-col items-center justify-center">
                <h1 className="font-mono text-5xl font-bold text-gray-900">{siteConfig.title}</h1>
                <h3 className="mt-4 font-mono text-xl  text-gray-900 ">{siteConfig.tagline}</h3>
                <div className="mt-5 flex gap-5">
                    <Link
                        className="button button--secondary button--lg my-5"
                        to="/docs/introduction/intro"
                    >
                        Get Started
                    </Link>
                </div>
            </div>
        </header>
    );
}

export default function Home() {
    const { siteConfig } = useDocusaurusContext();

    return (
        <Layout
            title={`${siteConfig.title} - Robot Arm Software `}
            description="Easy to use control system for robotic arms. Includes a user interface, control library and firmware"
        >
            <Head>
                <meta
                    name="description"
                    content="Comprehensive software solution for controlling and managing robot arms. Explore our advanced features and capabilities."
                />
                <script type="application/ld+json">
                    {JSON.stringify({
                        '@context': 'https://schema.org/',
                        '@type': 'Organization',
                        name: 'Robot Arm Software',
                        url: 'https://ribot.dev',
                    })}
                </script>
            </Head>
            <HomepageHeader />
            <main className="flex flex-col items-center justify-center gap-y-10">
                <HomepageFeatures />
                <div className="flex w-[80%] flex-col justify-center p-4">
                    <div className="flex flex-col gap-4 lg:flex-row">
                        <div className="flex-shrink">
                            <h1 className="my-4 self-start p-4 font-mono text-2xl font-bold">
                                {' '}
                                Easy to use Web Interface
                            </h1>
                            <p className="mb-7 px-7 text-gray-700 dark:text-gray-300">
                                The web interface allows you to control the robot arm from any
                                device with a web browser. The interface is designed to be easy to
                                use and understand regardless of your experience level.
                            </p>
                            <img
                                src={GeneralGif}
                                alt="General Page"
                                className="flex-1 rounded-md border border-b-gray-700  shadow-sm shadow-gray-300"
                            />
                        </div>
                        <div>
                            <h1 className="mt-4 self-start p-4 font-mono text-2xl font-bold">
                                {' '}
                                Python Development Library
                            </h1>
                            <p className="mb-7 px-7 text-gray-700 dark:text-gray-300">
                                The python library allows you to control the robot arm from your own
                                python scripts. The library is designed to be easy to use and
                                understand, perfect for beginners and experts alike.
                            </p>
                            <CodeBlock className="flex-1" language="python">{`
from ribot.control.arm_kinematics import ArmParameters, ArmPose
from ribot.controller import ArmController, Settings

if __name__ == "__main__":
    # Arm parameters (Physical dimensions of the arm)
    arm_params: ArmParameters = ArmParameters()
    arm_params.a2x = 0
    arm_params.a2z = 172.48
    arm_params.a3z = 173.5
    arm_params.a4z = 0
    arm_params.a4x = 126.2
    arm_params.a5x = 64.1
    arm_params.a6x = 169

    controller = ArmController(arm_parameters=arm_params)
    controller.start(websocket_server=False, wait=True)

    controller.set_setting_joints(Settings.STEPS_PER_REV_MOTOR_AXIS, 400)
    controller.home()

    # Move to a position
    position = ArmPose(x=320, y=0, z=250, pitch=0, roll=0, yaw=0)
    controller.move_to(position)
    controller.wait_done_moving()

    # Move to angles (rads)
    angles = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    controller.move_joints_to(angles)

    # Move the tool (rads)
    controller.set_tool_value(1.2)

    print("Homed:", controller.is_homed)


                            `}</CodeBlock>
                        </div>
                    </div>
                </div>
            </main>
        </Layout>
    );
}
