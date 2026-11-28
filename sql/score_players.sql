
WITH scaled AS (
  SELECT
    player,
    club,
    age,
    position,
    value_gbp_m,
    (kp_p90     - MIN(kp_p90)     OVER ()) / (MAX(kp_p90)     OVER () - MIN(kp_p90)     OVER ()) * 100 AS kp_score,
    (tb_p90     - MIN(tb_p90)     OVER ()) / (MAX(tb_p90)     OVER () - MIN(tb_p90)     OVER ()) * 100 AS tb_score,
    (prgp_p90   - MIN(prgp_p90)   OVER ()) / (MAX(prgp_p90)   OVER () - MIN(prgp_p90)   OVER ()) * 100 AS prgp_score,
    (xag_p90    - MIN(xag_p90)    OVER ()) / (MAX(xag_p90)    OVER () - MIN(xag_p90)    OVER ()) * 100 AS xag_score,
    (tklint_p90 - MIN(tklint_p90) OVER ()) / (MAX(tklint_p90) OVER () - MIN(tklint_p90) OVER ()) * 100 AS tklint_score
  FROM players
)
SELECT
  player,
  club,
  age,
  position,
  value_gbp_m,
  ROUND((
      kp_score     * 0.25
    + tb_score     * 0.20
    + prgp_score   * 0.20
    + xag_score    * 0.15
    + tklint_score * 0.20
  )::numeric, 1) AS total_score
FROM scaled
ORDER BY total_score DESC
LIMIT 20;