middleware leggero basato su Flask che permette di sincronizzare automaticamente 
il tracking number delle spedizioni ShippyPro con gli ordini Allegro.
Quando una spedizione viene generata su ShippyPro, quest’ultimo invia un webhook: 
il server intercetta l’evento, verifica che l’ordine provenga da Allegro e aggiorna il tracking tramite le API ufficiali Allegro.
