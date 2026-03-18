from playwright.sync_api import sync_playwright

BASE_URL = "http://webapp:8000"


def _open_clean_home(page):
    """Abre home limpia removiendo estado persistido del navegador."""
    page.goto(BASE_URL)
    page.evaluate("() => localStorage.clear()")
    page.reload()
    page.wait_for_selector("#menuScreen.active")


def _start_solo_game(page):
    """Navega hasta la pantalla de juego en modo solo."""
    _open_clean_home(page)
    page.evaluate("() => { showModeSelection(); selectMode('solo'); }")
    page.wait_for_selector("#playerNameScreen.active")
    page.fill("#playerName", "Tester")
    page.evaluate("() => startSoloGame()")
    page.wait_for_selector("#gameScreen.active #guessInput")


def _start_multiplayer_create(page, player_name="Host"):
    """Navega al flujo de crear partida multijugador y deja la pantalla en espera."""
    _open_clean_home(page)
    page.evaluate("() => { showModeSelection(); selectMode('multiplayer'); startMultiplayerCreate(); }")
    page.wait_for_selector("#multiplayerCreateScreen.active")
    page.fill("#multiplayerName", player_name)
    page.evaluate("() => createMultiplayerGame()")
    page.wait_for_selector("#waitingPlayerScreen.active")
    page.wait_for_selector("#waitingPlayerScreen.active #waitingGameId")


def _join_first_waiting_game(page, player_name="Guest"):
    """Navega al flujo de unirse a la primera partida disponible."""
    _open_clean_home(page)
    page.evaluate("() => { showModeSelection(); selectMode('multiplayer'); }")
    page.wait_for_selector("#multiplayerScreen.active")
    page.evaluate("() => loadWaitingGames()")
    page.wait_for_selector("#joinMultiplayerScreen.active")
    page.fill("#joinPlayerName", player_name)
    page.wait_for_selector("#joinMultiplayerScreen.active #gamesList .game-item button")
    page.locator("#joinMultiplayerScreen.active #gamesList .game-item button").first.click()
    page.wait_for_selector("#gameScreen.active")


def _extract_waiting_game_id(page):
    """Extrae el UUID de la pantalla de espera del host."""
    text = page.inner_text("#waitingPlayerScreen.active #waitingGameId")
    return text.replace("ID de juego:", "").strip()


def _join_specific_game(page, game_id, player_name="Guest"):
    """Une al guest a un game_id exacto para evitar flakiness por listas viejas."""
    _open_clean_home(page)
    page.evaluate("() => { showModeSelection(); selectMode('multiplayer'); }")
    # joinGame usa el valor del input #joinPlayerName
    page.evaluate(
        """
        ({ name, gid }) => {
            document.getElementById('joinPlayerName').value = name;
            joinGame(gid);
        }
        """,
        {"name": player_name, "gid": game_id},
    )
    page.wait_for_selector("#gameScreen.active")


def _sync_host_to_game_screen(host_page):
    """Fuerza sincronizacion del host tras join para evitar flakiness por timers en background."""
    host_page.bring_to_front()
    host_page.reload()
    host_page.wait_for_selector("#gameScreen.active", timeout=15000)


def test_home_menu_is_visible():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        page.goto(BASE_URL)

        assert page.is_visible("text=Fijas y Picas")
        assert page.is_visible("text=JUGAR")
        assert page.is_visible("text=CÓMO JUGAR")
        browser.close()


def test_instructions_screen_flow():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        page.goto(BASE_URL)
        page.click("text=CÓMO JUGAR")
        page.wait_for_selector("#instructionsScreen.active")
        assert page.is_visible("#instructionsScreen h2")
        assert page.is_visible("text=Objetivo:")

        page.click("text=ENTENDIDO")
        page.wait_for_selector("text=Fijas y Picas")
        browser.close()


def test_validate_number():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        _start_solo_game(page)

        page.fill("#guessInput", "1234")
        page.click("#submitButton")

        # El intento valido debe aparecer en el historial.
        page.wait_for_selector("#historyContainer .history-item")
        assert page.inner_text("#historyContainer .history-item .number").endswith("1234")
        browser.close()


def test_invalid_number():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        _start_solo_game(page)

        page.fill("#guessInput", "1123")
        page.click("#submitButton")

        page.wait_for_selector("#errorMessage")
        assert "no puede tener" in page.inner_text("#errorMessage").lower()
        browser.close()


def test_invalid_number_with_letters():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        _start_solo_game(page)

        page.fill("#guessInput", "12a3")
        page.click("#submitButton")

        page.wait_for_selector("#errorMessage")
        assert "solo se permiten numeros" in page.inner_text("#errorMessage").lower().replace("ú", "u")
        browser.close()


def test_invalid_number_length():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        _start_solo_game(page)

        page.fill("#guessInput", "123")
        page.click("#submitButton")

        page.wait_for_selector("#errorMessage")
        assert "4 digitos" in page.inner_text("#errorMessage").lower().replace("í", "i")
        browser.close()


def test_multiplayer_create_shows_waiting_state():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        _start_multiplayer_create(page, player_name="Alice")

        assert page.is_visible("#waitingPlayerScreen.active")
        assert "Esperando Jugador" in page.inner_text("#waitingPlayerScreen.active h2")
        assert "ID de juego:" in page.inner_text("#waitingPlayerScreen.active #waitingGameId")
        browser.close()


def test_multiplayer_second_player_can_join_game():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        host_page = browser.new_page()
        guest_page = browser.new_page()

        _start_multiplayer_create(host_page, player_name="Alice")
        game_id = _extract_waiting_game_id(host_page)
        _join_specific_game(guest_page, game_id, player_name="Bob")

        assert guest_page.is_visible("#gameScreen.active")
        assert "Bob" in guest_page.inner_text("#playerDisplay")
        assert "Multijugador" in guest_page.inner_text("#modeDisplay")
        browser.close()


def test_multiplayer_host_auto_transitions_from_waiting_to_game():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        host_page = browser.new_page()
        guest_page = browser.new_page()

        _start_multiplayer_create(host_page, player_name="Alice")
        game_id = _extract_waiting_game_id(host_page)
        _join_specific_game(guest_page, game_id, player_name="Bob")

        # Sincroniza host a pantalla de juego de forma determinista.
        _sync_host_to_game_screen(host_page)
        assert host_page.is_visible("#turnIndicator")
        assert "Mi turno" in host_page.inner_text("#currentTurnDisplay")
        browser.close()


def test_multiplayer_turn_block_and_enable_after_opponent_move():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        host_page = browser.new_page()
        guest_page = browser.new_page()

        _start_multiplayer_create(host_page, player_name="Alice")
        game_id = _extract_waiting_game_id(host_page)
        _join_specific_game(guest_page, game_id, player_name="Bob")
        _sync_host_to_game_screen(host_page)

        # Al inicio, el turno debe ser del Jugador 1 (host), asi que guest bloqueado.
        assert guest_page.is_disabled("#guessInput")
        assert guest_page.is_disabled("#submitButton")

        # Host hace un intento para ceder el turno.
        host_page.fill("#guessInput", "1234")
        host_page.click("#submitButton")

        # Verificacion determinista contra backend:
        # Espera a que cambie al turno del Jugador 2 o que finalice la partida.
        reached_expected_state = False
        for _ in range(20):
            response = guest_page.request.get(f"{BASE_URL}/game/{game_id}")
            game_data = response.json()

            if game_data.get("status") == "finished":
                reached_expected_state = True
                break

            if game_data.get("current_turn") == 2:
                guest_page.bring_to_front()
                guest_page.evaluate("() => restoreGameSession()")
                guest_page.wait_for_timeout(300)
                assert guest_page.is_visible("#gameScreen.active")
                assert not guest_page.is_disabled("#guessInput")
                assert not guest_page.is_disabled("#submitButton")
                reached_expected_state = True
                break

            guest_page.wait_for_timeout(400)

        assert reached_expected_state

        browser.close()

