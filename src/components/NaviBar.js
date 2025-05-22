import { useState } from 'react';
import { Navbar, Nav, Button, Modal, Form } from 'react-bootstrap';

export default function NaviBar() {
  const [showModal, setShowModal] = useState(false);
  const [teamData, setTeamData] = useState({
    name: '',
    email: '',
    password: ''
  });

  const handleShow = () => setShowModal(true);
  const handleClose = () => setShowModal(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setTeamData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      // Отправка данных на бэкенд FastAPI
      const response = await fetch('http://your-fastapi-backend/api/teams/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(teamData)
      });

      if (response.ok) {
        const result = await response.json();
        console.log('Команда зарегистрирована:', result);
        handleClose();
        // Здесь можно добавить обновление таблицы или редирект
      } else {
        console.error('Ошибка регистрации');
      }
    } catch (error) {
      console.error('Ошибка:', error);
    }
  };

  return (
    <>
      <Navbar collapseOnSelect expand="lg" bg="dark" variant="dark">
        <Navbar.Brand>Сервис для проведения конкурсов по ИИ</Navbar.Brand>
        <Navbar.Toggle aria-controls="responsive-navbar-nav"/>
        <Navbar.Collapse id="responsive-navbar-nav">
          <Nav className="ms-auto">
            <Button 
              variant="primary" 
              className="me-2"
              onClick={handleShow}
            >
              Участвовать в конкурсе
            </Button>
          </Nav>
        </Navbar.Collapse>
      </Navbar>

      {/* Модальное окно для регистрации команды */}
      <Modal show={showModal} onHide={handleClose}>
        <Modal.Header closeButton>
          <Modal.Title>Регистрация команды</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form onSubmit={handleSubmit}>
            <Form.Group className="mb-3">
              <Form.Label>Название команды</Form.Label>
              <Form.Control
                type="text"
                name="name"
                value={teamData.name}
                onChange={handleInputChange}
                required
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Email</Form.Label>
              <Form.Control
                type="email"
                name="email"
                value={teamData.email}
                onChange={handleInputChange}
                required
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Пароль</Form.Label>
              <Form.Control
                type="password"
                name="password"
                value={teamData.password}
                onChange={handleInputChange}
                required
              />
            </Form.Group>

            <div className="d-flex justify-content-end">
              <Button variant="secondary" onClick={handleClose} className="me-2">
                Отмена
              </Button>
              <Button variant="primary" type="submit">
                Зарегистрироваться
              </Button>
            </div>
          </Form>
        </Modal.Body>
      </Modal>
    </>
  );
}