import useDocusaurusContext from "@docusaurus/useDocusaurusContext";
import Layout from "@theme/Layout";
import Link from "@docusaurus/Link";
import HomepageFeatures from "@site/src/components/HomepageFeatures";

function HomepageHeader() {
  const { siteConfig } = useDocusaurusContext();
  return (
    <header className="w-full bg-orange-400 h-60">
      <div className="w-full flex flex-col items-center h-full justify-center">
        <h1 className="text-5xl font-bold text-gray-800">{siteConfig.title}</h1>
        <h3 className="mt-4 text-xl  text-gray-800">{siteConfig.tagline}</h3>
        <div className="flex gap-5 mt-5">
        <Link className='mt-5 button button--secondary button--lg' to='/docs/intro'>Get Started</Link>
      </div>

      </div>
    </header>
  );
}

export default function Home() {
  const { siteConfig } = useDocusaurusContext();
  return (
    <Layout
      title={`Hello from ${siteConfig.title}`}
      description="Description will go into a meta tag in <head />"
    >
      <HomepageHeader />
      <main>
        <HomepageFeatures />
      </main>
    </Layout>
  );
}
