bomberman
=========


private void killAllNear(List<Blast> blasts) {
/* 218 */     killHeroes(blasts);
/* 219 */     killPerks(blasts);
/* 220 */     killWalls(blasts);
/*     */   }



/*     */   public void tickField() {
/* 108 */     applyAllHeroes();         // Players moves - move, put bombs, pick perks
/* 109 */     meatChopperEatHeroes();   // kill players who moved to chopper
/* 110 */     this.walls.tick();        // move choppers (chopers are Wall class)
/* 111 */     meatChopperEatHeroes();   // eat players if found
/* 112 */     tactAllBombs();           // process bombs:
/* 113 */     tactAllPerks();           // process perks
/* 114 */     tactAllHeroes();          // owned perks tick
/*     */   }

tactAllBombs:
 - if not RC: timer--, boom if timer==0