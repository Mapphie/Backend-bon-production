from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from app.database.database import SyncSession

router = APIRouter()


class BonProduction(BaseModel):
    id: Optional[str] = None
    
    code_couleur: Optional[str] = None
    code_produit_gamme: Optional[str] = None
    numero_machine: Optional[str] = None
    pl_status: Optional[str] = None
    code_produit_bien: Optional[str] = None
    couleur: Optional[str] = None
    numero_planning: Optional[str] = None
    total_qte_a_traiter_sur_oa: Optional[float] = None
    reliquat: Optional[float] = None
    reliquat_oa: Optional[float] = None
    qte_a_dispatcher: Optional[float] = None
    qte_extra: Optional[float] = None
    lumps_en_kg: Optional[float] = None
    compteur_debut: Optional[float] = None
    compteur_fin: Optional[float] = None
    nb_jets: Optional[float] = None
    qte_rejetee: Optional[float] = None
    runner_en_kg: Optional[float] = None
    total_produit: Optional[float] = None
    date_fabrication: Optional[datetime] = None
    numero_bon_fabrication: Optional[str] = None
    numero_ordre_fabrication_extra: Optional[str] = None
    numero_bon_fabrication_extra: Optional[str] = None
    pct_extra: Optional[float] = None
    numero_bon_fabrication_regrind: Optional[str] = None
    numero_bon_livraison_interne_regrind: Optional[str] = None
    numero_bon_entree_valorise_regrind: Optional[str] = None
    traite: Optional[str] = None
    utilisateur: Optional[str] = None
    valideur: Optional[str] = None
    date_heure_traitement: Optional[datetime] = None
    date_enregistrement: Optional[datetime] = None
    
    
@router.post("/production")
def inserer_bon(bon: BonProduction):
        with SyncSession as db:
            try:
                if bon.id:
                    update_query = text("""
                        UPDATE _PRODUCTION SET [CODE COULEUR] = :code_couleur,[CODE DU PRODUIT GAMME] = :code_produit_gamme,[NUMERO MACHINE] = :numero_machine,[PL STATUS] = :pl_status,
                        [CODE DU PRODUIT BIEN] = :code_produit_bien,[COULEUR] = :couleur,[N DE PLANNING] = :numero_planning,[TOTAL QTE A TRAITER SUR OA] = :total_qte_a_traiter_sur_oa,
                        [RELIQUAT] = :reliquat,[RELIQUAT OA] = :reliquat_oa,[QTE A DISPATCHER] = :qte_a_dispatcher,[QTE EXTRA] = :qte_extra,[LUMPS EN KG] = :lumps_en_kg,
                        [COMPTEUR DEBUT] = :compteur_debut,[COMPTEUR FIN] = :compteur_fin,[NB JETS] = :nb_jets,[QTE REJETEE] = :qte_rejetee,[RUNNER EN KG] = :runner_en_kg,
                        [TOTAL PRODUIT] = :total_produit,[DATE DE FABRICATION] = :date_fabrication,[pct EXTRA] = :pct_extra,[UTILISATEUR] = :utilisateur,[VALIDEUR] = :valideur,
                        [DATE D'ENREGISTREMENT] = :date_enregistrement WHERE id = :id              
                    """)
                    
                    result = db.execute(update_query, bon.model_dump())
                    
                    if result.rowcount == 0:
                        raise HTTPException(status_code=404, detail=f"Bon {bon.id} introuvable")
                    
                    db.commit()
                    return {"id":bon.id, "action": "update"}
                
                else:
                    insert_query = text("""
                    INSERT INTO _PRODUCTION (
                        [CODE COULEUR],[CODE DU PRODUIT GAMME],[NUMERO MACHINE],[PL STATUS],[CODE DU PRODUIT BIEN],
                        [COULEUR],[N DE PLANNING],[TOTAL QTE A TRAITER SUR OA],[RELIQUAT],[RELIQUAT OA],
                        [QTE A DISPATCHER],[QTE EXTRA],[LUMPS EN KG],
                        [COMPTEUR DEBUT],[COMPTEUR FIN],[NB JETS],[QTE REJETEE],
                        [RUNNER EN KG],[TOTAL PRODUIT],[DATE DE FABRICATION],
                        [pct EXTRA],[UTILISATEUR],[VALIDEUR],[DATE D'ENREGISTREMENT]
                    )
                    OUTPUT INSERTED.id
                    VALUES (
                        :code_couleur, :code_produit_gamme, :numero_machine, :pl_status, :code_produit_bien,
                        :couleur, :numero_planning, :total_qte_a_traiter_sur_oa, :reliquat, :reliquat_oa,
                        :qte_a_dispatcher, :qte_extra, :lumps_en_kg,
                        :compteur_debut, :compteur_fin, :nb_jets, :qte_rejetee,
                        :runner_en_kg, :total_produit, :date_fabrication,
                        :pct_extra, :utilisateur, :valideur, :date_enregistrement
                    )
                    """)
                    
                    result = db.execute(insert_query, bon.model_dump())
                    new_id = result.scalar()
                    
                    db.commit()
                    return {"id": str(new_id), "action": "insert"}
                
            except HTTPException:
                db.rollback()
                raise
            except Exception as e:
                db.rollback()
                raise HTTPException(status_code=500, detail=f"Erreur enregistrement bon : {e}")
        
@router.patch("/production/{bon_id}/traitement")
def traiter_bon(bon_id: str, bon: BonProduction):
        with SyncSession as db:
            try:
                update_query = text("""
                    UPDATE _PRODUCTION SET
                        [NUMERO BON DE FABRICATION] = :numero_bon_fabrication,
                        [NUMERO ORDRE DE FABRICATION EXTRA] = :numero_ordre_fabrication_extra,
                        [NUMERO BON DE FABRICATION EXTRA] = :numero_bon_fabrication_extra,
                        [NUMERO BON DE FABRICATION REGRIND] = :numero_bon_fabrication_regrind,
                        [NUMERO DE BON LIVRAISON INTERNE REGRIND] = :numero_bon_livraison_interne_regrind,
                        [NUMERO DE BON D'ENTREE VALORISE REGRIND] = :numero_bon_entree_valorise_regrind,
                        [TRAITE] = :traite,
                        [DATE/HEURE TRAITEMENT] = :date_heure_traitement
                    WHERE id = :id
                """)
                params = bon.model_dump()
                params["id"] = bon_id
                
                result = db.execute(update_query, params)

                if result.rowcount == 0:
                    raise HTTPException(status_code=404, detail=f"Bon {bon_id} introuvable")

                db.commit()
                return {"id": bon_id, "action": "traitement"}

            except HTTPException:
                db.rollback()
                raise
            except Exception as e:
                db.rollback()
                raise HTTPException(status_code=500, detail=f"Erreur traitement bon : {e}")