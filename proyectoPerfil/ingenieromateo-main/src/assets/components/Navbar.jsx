import React from "react";
import {
  Navbar,
  NavbarBrand,
  NavbarMenuToggle,
  NavbarMenuItem,
  NavbarMenu,
  NavbarContent,
} from "@nextui-org/react";
import { Link } from "react-router-dom";
import "../styles/stylePerfil.css";
import {
  Award,
  HomeIcon,
  FolderCheck,
  UserSearch,
  ContactRound,
} from "lucide-react";
import { Avatar, Image } from "@nextui-org/react";
import fotoPerfil from "../images/Foto.jpeg";

const NavbarComponente = () => {
  const [isMenuOpen, setIsMenuOpen] = React.useState(false);

  const menuItems = [
    "Inicio",
    "Habilidades",
    "Proyectos",
    "Acerca de mi",
    "Contactoss",
  ];

  return (
    <Navbar
      isBordered
      isMenuOpen={isMenuOpen}
      onMenuOpenChange={setIsMenuOpen}
      className="rounded rounded-md bg-gray-800 text-gray-300"
    >
      <NavbarContent className="sm:hidden" justify="start">
        <NavbarMenuToggle
          aria-label={isMenuOpen ? "Close menu" : "Open menu"}
        />
      </NavbarContent>

      <NavbarContent className="sm:hidden pr-3 w-46" justify="center">
        <NavbarBrand>
          <Avatar size="xl" src={fotoPerfil} />
          <p className="font-bold text-inherit">
            {" "}
            Ingeniero Electrico de Manizales
          </p>
        </NavbarBrand>
      </NavbarContent>

      <NavbarContent className="hidden sm:flex gap-4" justify="center">
        <NavbarMenuItem className="hover:text-pink-200">
          <Link to="/">
            <HomeIcon />
            Inicio
          </Link>
        </NavbarMenuItem>
        <NavbarMenuItem className="hover:text-pink-200">
          <Link to="/habilidades">
            <Award />
            Habilidades
          </Link>
        </NavbarMenuItem>
        <NavbarMenuItem>
          <Link to="/proyectos">
            <FolderCheck />
            Proyectos
          </Link>
        </NavbarMenuItem>
        <NavbarMenuItem key="Acerca de mi">
          <Link to="/acerca">
            <UserSearch />
            Acerca de mi
          </Link>
        </NavbarMenuItem>
        <NavbarMenuItem key="Contacto">
          <Link to="/contacto">
            <ContactRound />
            Contacto
          </Link>
        </NavbarMenuItem>
      </NavbarContent>

      <NavbarMenu className="w-48 max-h-fit rounded-lg mt-2 backdrop-blur-[10px] ">
        <NavbarMenuItem key="Inicio">
          <Link to="/" onClick={() => setIsMenuOpen(false)}>
            <p>
              <HomeIcon />
              Inicio
            </p>
          </Link>
        </NavbarMenuItem>
        <NavbarMenuItem key="Habilidades">
          <Link to="/habilidades" onClick={() => setIsMenuOpen(false)}>
            <Award />
            Habilidades
          </Link>
        </NavbarMenuItem>
        <NavbarMenuItem key="Proyectos">
          <Link to="/proyectos" onClick={() => setIsMenuOpen(false)}>
            <FolderCheck />
            Proyectos
          </Link>
        </NavbarMenuItem>
        <NavbarMenuItem key="Acerca de mi">
          <Link to="/acerca" onClick={() => setIsMenuOpen(false)}>
            <UserSearch />
            Acerca de mi
          </Link>
        </NavbarMenuItem>
        <NavbarMenuItem key="Contacto">
          <Link to="/contacto" onClick={() => setIsMenuOpen(false)}>
            <ContactRound />
            Contacto
          </Link>
        </NavbarMenuItem>
      </NavbarMenu>
    </Navbar>
  );
};

export default NavbarComponente;
