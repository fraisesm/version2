import React from 'react';
import { Navbar, Nav, Button } from 'react-bootstrap';
import { Link } from 'react-router-dom';

export default function NaviBar() {
    return (
    <>  
      <Navbar collapseOnSelect expand="lg" bg="dark" variant="dark">
          <Navbar.Brand>Сервис для проведения конкурсов по ИИ</Navbar.Brand>
          <Navbar.Toggle aria-controls="responsive-navbar-nav"/>
          <Navbar.Collapse id="responsive-navbar-nav">
               <Nav className="ms-auto">
                   <Button variant="primary" className="me-2">Участвовать в конкурсе</Button>
               </Nav>
          </Navbar.Collapse>
      </Navbar>
    </>
    )
}