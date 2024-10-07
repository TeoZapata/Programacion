import TrabajosCard from "../components/Card";

export default function Inicio() {
  return (
    <section id="title" className="General-Container">
      <h1 className="perfil-title text-xl  ">Hola, Soy Mateo Salazar Zapata</h1>
      <p className="text-left">
        Ingeniero eléctrico con un{" "}
        <span className="font-medium">perfil multidisciplinario</span>. Mi
        formación académica, ​complementada con la experiencia práctica en el
        sector eléctrico, me ha ​dotado de las herramientas necesarias para
        adaptarme a diferentes entornos y ​proyectos. Desde el{" "}
        <span className="font-medium">
          diseño de sistemas eléctricos residenciales y comerciales
        </span>{" "}
        ​hasta el desarrollo de herramientas de{" "}
        <span className="font-medium">
          análisis de datos utilizando Python y ​Flask
        </span>
        , mi experiencia abarca un amplio espectro de la ingeniería eléctrica.
        Mi ​pasión por esta disciplina, cultivada desde mis inicios en el ITEC,
        me impulsa a ​buscar soluciones creativas y eficientes para los desafíos
        energéticos actuales.
      </p>

      <div className="grid grid-cols-2 gap-4">
        {TrabajosCard(
          "https://nextui.org/images/hero-card-complete.jpeg",
          "jaja"
        )}
        <div>
          <TrabajosCard />
        </div>
        <div>
          <TrabajosCard />
        </div>
        <div>
          <TrabajosCard />
        </div>
        <div>
          <TrabajosCard />
        </div>
        <div>
          <TrabajosCard />
        </div>
        <div>
          <TrabajosCard />
        </div>
        <div>
          <TrabajosCard />
        </div>
      </div>
    </section>
  );
}
