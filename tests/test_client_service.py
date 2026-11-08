from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.services.client_service import supprimer_client


def test_supprimer_client_avec_commandes_refuse():
    db = MagicMock()

    client = SimpleNamespace(
        id=1,
        commandes=[SimpleNamespace(id=10)]
    )

    db.scalar.return_value = client

    with pytest.raises(HTTPException) as erreur:
        supprimer_client(db, 1)

    assert erreur.value.status_code == 409
    db.delete.assert_not_called()
    db.commit.assert_not_called()


def test_supprimer_client_sans_commandes_autorise():
    db = MagicMock()

    client = SimpleNamespace(
        id=2,
        commandes=[]
    )

    db.scalar.return_value = client

    supprimer_client(db, 2)

    db.delete.assert_called_once_with(client)
    db.commit.assert_called_once()