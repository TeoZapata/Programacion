import { Accordion, AccordionItem } from "@nextui-org/react";
export default function Proyecto() {
  const defaultContent =
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.";

  return (
    <section className="General-Container" id="proyecto">
      <h1 className="perfil-title">Proyectos Destacados</h1>
      <p>
        A lo largo de mi trayectoria profesional, he establecido sólidas
        relaciones con mis clientes, brindando servicios de alta calidad y
        ​confiabilidad. Mi participación en proyectos de gran envergadura, como
        la renovación de 42 subestaciones en el marco del Plan ​Maestro de la
        Sede Bogotá, me ha permitido demostrar mi capacidad para manejar grandes
        volúmenes de datos, diseñar sistemas ​de monitoreo eficientes y
        coordinar equipos de trabajo. Además, mi experiencia en proyectos de
        campo, desde el diseño hasta la ​instalación, me ha brindado una visión
        integral de los sistemas eléctricos y me ha permitido satisfacer las
        necesidades específicas ​de cada cliente.
      </p>
      <Accordion variant="bordered">
        <AccordionItem
          key="1"
          aria-label="Accordion 1"
          title="Plan Maestro Renovación y Modernizacion Subestaciones Eléctricas, Unal Sede Bogota"
        >
          {defaultContent}
        </AccordionItem>
        <AccordionItem
          key="2"
          aria-label="Accordion 2"
          title="Instalaciones Electricas Manizales"
        >
          {defaultContent}
        </AccordionItem>
        <AccordionItem
          key="3"
          aria-label="Accordion 3"
          title="Proyectos Personales"
        >
          {defaultContent}
        </AccordionItem>
      </Accordion>
    </section>
  );
}
