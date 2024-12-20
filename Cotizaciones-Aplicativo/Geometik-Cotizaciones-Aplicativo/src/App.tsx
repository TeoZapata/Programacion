import { Route, Routes } from "react-router-dom";

import InicioPage from "@/pages/index";
import IniciarCotizacionesPage from "@/pages/docs";
import HistorialCotizacionesPage from "@/pages/pricing";
import ListadoPreciosPage from "@/pages/blog";
import AboutPage from "@/pages/about";

function App() {
  return (
    <Routes>
      <Route element={<InicioPage />} path="/" />
      <Route element={<IniciarCotizacionesPage />} path="/IniciarCotizacion" />
      <Route
        element={<HistorialCotizacionesPage />}
        path="/HistorialDeCotizaciones"
      />
      <Route element={<ListadoPreciosPage />} path="/ListadoDePrecios" />
      <Route element={<AboutPage />} path="/AcercaDe" />
    </Routes>
  );
}

export default App;
