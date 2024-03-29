const FeatureList = [
    {
        title: 'Easy to Use Interface',
        Svg: require('@site/static/img/exp.svg').default,
        description: (
            <>
                Powerful User Interface that allows you to control your robot arm with just a few
                clicks.
            </>
        ),
    },
    {
        title: 'Controller Library',
        Svg: require('@site/static/img/python.svg').default,
        description: (
            <>
                There is space for growth, first learn the GUI and then use the controller library
                to control your robot arm from your own code.
            </>
        ),
    },
    {
        title: 'Focus on What Matters',
        Svg: require('@site/static/img/docker.svg').default,
        description: (
            <>
                Powered by Docker, RiBot allows you to focus on your robot arm and not the
                infrastructure.
            </>
        ),
    },
];

function Feature({ Svg, title, description }) {
    return (
        <div className="my-4 flex w-4/5 flex-col rounded-md border border-gray-400 px-4 py-3  shadow-sm shadow-gray-500 lg:w-1/4">
            <div className="flex items-center justify-center">
                <Svg className="h-40 w-full" role="img" />
            </div>
            <div className="text-center">
                <h3 className="text-xl font-bold">{title}</h3>
                <p>{description}</p>
            </div>
        </div>
    );
}

export default function HomepageFeatures() {
    return (
        <section>
            <div className="flex w-full flex-wrap items-center justify-center gap-x-3">
                {FeatureList.map((props, idx) => (
                    <Feature key={idx} {...props} />
                ))}
            </div>
        </section>
    );
}
