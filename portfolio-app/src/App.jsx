import Hero from "./components/Hero.jsx";
import Summary from "./components/Summary.jsx";
import Outcomes from "./components/Outcomes.jsx";
import Experience from "./components/Experience.jsx";
import Skills from "./components/Skills.jsx";
import Education from "./components/Education.jsx";
import Writing from "./components/Writing.jsx";
import Footer from "./components/Footer.jsx";
import SectionNav from "./components/SectionNav.jsx";

export default function App() {
  return (
    <>
      <SectionNav />
      <main className="max-w-content mx-auto px-6 pt-12 sm:pt-20 lg:pt-24 pb-12">
        <Hero />
        <Summary />
        <Outcomes />
        <Experience />
        <Skills />
        <Education />
        <Writing />
      </main>
      <Footer />
    </>
  );
}
