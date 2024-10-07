import "../styles/stylePerfil.css";
const AcercaDeMi = () => {
  return (
    <section className="General-Container">
      <div className="container">
        <h2 className="titulo">Acerca de Mí</h2>

        <div className="contenido">
          <div className="imagen">
            {/* Agrega tu imagen aquí */}
            <img src="/ruta/a/tu/imagen.jpg" alt="Tu nombre" />
          </div>

          <div className="texto">
            <p>
              {/* Escribe una breve descripción sobre ti */}
              Soy un apasionado desarrollador web con experiencia en [menciona
              tus habilidades y experiencia]. Me encanta aprender nuevas
              tecnologías y crear soluciones innovadoras.
            </p>

            <p>
              {/* Agrega más información relevante */}
              En mi tiempo libre disfruto de [menciona tus hobbies e intereses].
            </p>

            {/* Puedes agregar más secciones como: */}
            {/* <h3>Experiencia</h3> */}
            {/* <ul> */}
            {/*  <li>Experiencia 1</li> */}
            {/*  <li>Experiencia 2</li> */}
            {/* </ul> */}

            {/* <h3>Educación</h3> */}
            {/* <p>Nombre de la institución - Título</p> */}

            {/* <h3>Contacto</h3> */}
            {/* <p>Correo electrónico: tu.correo@email.com</p> */}
          </div>
        </div>
      </div>
    </section>
  );
};

export default AcercaDeMi;
