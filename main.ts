// ============================================================
//  ARIA: STAR KEEPER
//  MakeCode Arcade space shooter
//
//  Controls: D-pad = move  |  A = shoot laser
//  Goal:     Reach 500 pts to win — collect gems (+50),
//            blast enemies (+10 / +20 / +150). You have 3 lives.
//  New:      Fast enemies, temporary shield power-up, mini-boss wave.
// ============================================================

namespace SpriteKind {
    export const PowerUp = SpriteKind.create()
    export const FastEnemy = SpriteKind.create()
    export const Boss = SpriteKind.create()
}

// ── Splash screen ────────────────────────────────────────────
game.splash("ARIA: STAR KEEPER", "A = shoot  ★  Reach 500 pts!")

// ── Scene ────────────────────────────────────────────────────
scene.setBackgroundColor(9)

// ── State ────────────────────────────────────────────────────
const WIN_SCORE = 500
let enemySpeed = 55
let lastSpeedCheckScore = 0
let lastLifeScore = 0
let shieldUntil = 0
let bossSpawned = false
let bossHp = 30

function shieldActive() {
    return game.runtime() < shieldUntil
}

function checkWin() {
    if (info.score() >= WIN_SCORE) {
        effects.confetti.startScreenEffect()
        game.over(true)
    }
}

// ── Player ship ──────────────────────────────────────────────
const player = sprites.create(img`
    . . . . . . . .
    . . . c c . . .
    . c c c c c c .
    c c c d 1 c c c
    . c c c c c c .
    . . . c c . . .
    . . . . . . . .
    . . . . . . . .
`, SpriteKind.Player)
player.setPosition(20, 60)
player.setFlag(SpriteFlag.StayInScreen, true)
controller.moveSprite(player, 100, 100)
info.setLife(3)
info.setScore(0)

// ── Shoot laser on A ─────────────────────────────────────────
controller.A.onEvent(ControllerButtonEvent.Pressed, () => {
    const laser = sprites.createProjectileFromSprite(img`
        . 6 .
        6 6 6
        . 6 .
    `, player, 210, 0)
    laser.setFlag(SpriteFlag.AutoDestroy, true)
    music.play(music.melodyPlayable(music.baDing), music.PlaybackMode.InBackground)
})

// ── Normal enemy wave ────────────────────────────────────────
game.onUpdateInterval(1500, () => {
    const enemy = sprites.create(img`
        . 2 . . . . 2 .
        2 2 . . . . 2 2
        2 2 2 2 2 2 2 2
        2 f 2 2 2 2 f 2
        2 2 2 2 2 2 2 2
        2 2 . . . . 2 2
        . 2 . . . . 2 .
        . . . . . . . .
    `, SpriteKind.Enemy)
    enemy.setPosition(170, randint(8, 112))
    enemy.setVelocity(-enemySpeed, 0)
    enemy.setFlag(SpriteFlag.AutoDestroy, true)
})

// ── Fast zig-zag enemy wave ──────────────────────────────────
game.onUpdateInterval(3200, () => {
    if (info.score() < 120) {
        return
    }
    const fastEnemy = sprites.create(img`
        . . 4 4 4 4 . .
        . 4 4 8 8 4 4 .
        4 4 8 8 8 8 4 4
        4 8 8 4 4 8 8 4
        4 4 8 8 8 8 4 4
        . 4 4 8 8 4 4 .
        . . 4 4 4 4 . .
        . . . . . . . .
    `, SpriteKind.FastEnemy)
    fastEnemy.setPosition(170, randint(12, 108))
    fastEnemy.setVelocity(-(enemySpeed + 35), randint(-35, 35))
    fastEnemy.setFlag(SpriteFlag.AutoDestroy, true)
    fastEnemy.setFlag(SpriteFlag.BounceOnWall, true)
    fastEnemy.setFlag(SpriteFlag.StayInScreen, true)
})

// ── Spawn crystal gems ───────────────────────────────────────
game.onUpdateInterval(4000, () => {
    const gem = sprites.create(img`
        . . . 9 9 . . .
        . . 9 b b 9 . .
        . 9 b 1 1 b 9 .
        . 9 b 1 1 b 9 .
        . . 9 b b 9 . .
        . . . 9 9 . . .
        . . . . . . . .
        . . . . . . . .
    `, SpriteKind.Food)
    gem.setPosition(170, randint(8, 112))
    gem.setVelocity(-40, 0)
    gem.setFlag(SpriteFlag.AutoDestroy, true)
})

// ── Spawn shield power-up ────────────────────────────────────
game.onUpdateInterval(9000, () => {
    if (shieldActive()) {
        return
    }
    const shieldOrb = sprites.create(img`
        . . 5 5 5 5 . .
        . 5 5 7 7 5 5 .
        5 5 7 7 7 7 5 5
        5 7 7 5 5 7 7 5
        5 7 7 5 5 7 7 5
        5 5 7 7 7 7 5 5
        . 5 5 7 7 5 5 .
        . . 5 5 5 5 . .
    `, SpriteKind.PowerUp)
    shieldOrb.setPosition(170, randint(10, 110))
    shieldOrb.setVelocity(-55, 0)
    shieldOrb.setFlag(SpriteFlag.AutoDestroy, true)
})

// ── Mini-boss wave at 250+ score ─────────────────────────────
game.onUpdateInterval(800, () => {
    if (bossSpawned || info.score() < 250) {
        return
    }

    bossSpawned = true
    bossHp = 30

    const boss = sprites.create(img`
        . 2 2 2 2 2 2 2 2 2 2 2 .
        2 2 2 4 4 4 4 4 4 2 2 2 2
        2 2 4 4 f 4 4 4 f 4 4 2 2
        2 4 4 4 4 4 4 4 4 4 4 4 2
        2 4 4 4 4 9 9 4 4 4 4 4 2
        2 4 4 4 4 9 9 4 4 4 4 4 2
        2 4 4 4 4 4 4 4 4 4 4 4 2
        2 2 4 4 4 4 4 4 4 4 4 2 2
        . 2 2 2 2 2 2 2 2 2 2 2 .
    `, SpriteKind.Boss)
    boss.setPosition(155, 60)
    boss.setVelocity(-20, 18)
    boss.setFlag(SpriteFlag.BounceOnWall, true)
    boss.setFlag(SpriteFlag.StayInScreen, true)
    music.play(music.melodyPlayable(music.bigCrash), music.PlaybackMode.InBackground)
    game.showLongText("WARNING: BOSS WAVE!", DialogLayout.Bottom)
})

// ── Laser hits normal enemy ──────────────────────────────────
sprites.onOverlap(SpriteKind.Projectile, SpriteKind.Enemy, (laser, enemy) => {
    laser.destroy()
    enemy.destroy(effects.fire, 500)
    info.changeScoreBy(10)

    const score = info.score()
    if (score - lastSpeedCheckScore >= 100) {
        lastSpeedCheckScore = score
        enemySpeed += 10
    }

    checkWin()
})

// ── Laser hits fast enemy ────────────────────────────────────
sprites.onOverlap(SpriteKind.Projectile, SpriteKind.FastEnemy, (laser, fastEnemy) => {
    laser.destroy()
    fastEnemy.destroy(effects.disintegrate, 350)
    info.changeScoreBy(20)
    checkWin()
})

// ── Laser hits boss ──────────────────────────────────────────
sprites.onOverlap(SpriteKind.Projectile, SpriteKind.Boss, (laser, boss) => {
    laser.destroy()
    bossHp -= 1
    boss.startEffect(effects.warmRadial, 60)
    if (bossHp <= 0) {
        boss.destroy(effects.fire, 1200)
        info.changeScoreBy(150)
        music.play(music.melodyPlayable(music.magicWand), music.PlaybackMode.InBackground)
        checkWin()
    }
})

function handlePlayerHit(enemy: Sprite) {
    enemy.destroy()

    if (shieldActive()) {
        player.startEffect(effects.rings, 150)
        music.play(music.melodyPlayable(music.zapped), music.PlaybackMode.InBackground)
        return
    }

    player.startEffect(effects.spray, 300)
    info.changeLifeBy(-1)
    music.play(music.melodyPlayable(music.smallCrash), music.PlaybackMode.InBackground)
}

// ── Player collides with enemies/boss ────────────────────────
sprites.onOverlap(SpriteKind.Player, SpriteKind.Enemy, (ship, enemy) => {
    handlePlayerHit(enemy)
})

sprites.onOverlap(SpriteKind.Player, SpriteKind.FastEnemy, (ship, fastEnemy) => {
    handlePlayerHit(fastEnemy)
})

sprites.onOverlap(SpriteKind.Player, SpriteKind.Boss, (ship, boss) => {
    if (shieldActive()) {
        bossHp -= 5
        boss.startEffect(effects.fire, 120)
        music.play(music.melodyPlayable(music.knock), music.PlaybackMode.InBackground)
        if (bossHp <= 0) {
            boss.destroy(effects.fire, 1200)
            info.changeScoreBy(150)
            checkWin()
        }
        return
    }

    info.changeLifeBy(-1)
    ship.startEffect(effects.spray, 300)
    music.play(music.melodyPlayable(music.smallCrash), music.PlaybackMode.InBackground)
})

// ── Collect gem ───────────────────────────────────────────────
sprites.onOverlap(SpriteKind.Player, SpriteKind.Food, (ship, gem) => {
    gem.destroy(effects.confetti, 500)
    info.changeScoreBy(50)
    music.play(music.melodyPlayable(music.powerUp), music.PlaybackMode.InBackground)
    checkWin()
})

// ── Collect shield orb ───────────────────────────────────────
sprites.onOverlap(SpriteKind.Player, SpriteKind.PowerUp, (ship, orb) => {
    orb.destroy(effects.trail, 250)
    shieldUntil = game.runtime() + 5000
    ship.startEffect(effects.halo, 250)
    music.play(music.melodyPlayable(music.powerUp), music.PlaybackMode.InBackground)
    game.showLongText("Shield online for 5 seconds!", DialogLayout.Bottom)
})

// ── Bonus life every 300 pts ──────────────────────────────────
game.onUpdateInterval(500, () => {
    const score = info.score()
    if (score > 0 && score - lastLifeScore >= 300) {
        lastLifeScore = score
        info.changeLifeBy(1)
        music.play(music.melodyPlayable(music.powerUp), music.PlaybackMode.InBackground)
    }
})
