import React from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import NavbarComponente from "./assets/components/Navbar";
import Proyecto from "./assets/pages/Proyectos";
import Habilidades from "./assets/pages/Habilidades";
import Inicio from "./assets/pages/Inicio";
import AcercaDeMi from "./assets/pages/AcercaDeMi";
import Contacto from "./assets/pages/Contacto";
import "./assets/styles/stylePerfil.css";

function App() {
  return (
    <div className="App-container">
      <Router>
        <NavbarComponente />
        <Routes>
          <Route exact path="/" element={<Inicio />} />
          <Route exact path="/acerca" element={<AcercaDeMi />} />
          <Route exact path="/proyectos" element={<Proyecto />} />
          <Route exact path="/habilidades" element={<Habilidades />} />
          <Route exact path="/contacto" element={<Contacto />} />
        </Routes>
      </Router>
    </div>
  );
}

export default App;
