import useBaseUrl from "@docusaurus/useBaseUrl";
import React from "react";
import clsx from "clsx";
import styles from "./HomepageFeatures.module.css";

type FeatureItem = {
  title: string;
  image: string;
  description: JSX.Element;
};

const FeatureList: FeatureItem[] = [
  {
    title: "Just ImageJ",
    image: "/img/undraw_docusaurus_mountain.svg",
    description: (
      <>
        MikroJ just wraps your ImageJ instance and exposes it to arkitekt. Use
        your ImageJ plugins as you would normally do.
      </>
    ),
  },
  {
    title: "Bundled or Development",
    image: "/img/undraw_docusaurus_tree.svg",
    description: (
      <>
        Do you plan to integrated your own macros or do you want to use a
        predefined set of community macros? You can choose both MikroJ
        Development or Bundled Edition
      </>
    ),
  },
  {
    title: "Build on PyImageJ",
    image: "/img/undraw_docusaurus_react.svg",
    description: (
      <>MikroJ is build upon PyImageJ, an amazing python to imagej bridge.</>
    ),
  },
];

function Feature({ title, image, description }: FeatureItem) {
  return (
    <div className={clsx("col col--4")}>
      <div className="text--center padding-horiz--md padding-top--md">
        <h3>{title}</h3>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures(): JSX.Element {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
