<?php

/**
 * CurrentVersion renders the running PRADO framework version inline.
 *
 * It reads the version from {@see \Prado\Prado::getVersion()} so quickstart prose
 * and sample output track the installed framework instead of a hardcoded string.
 * Use it inline, for example: PRADO <com:CurrentVersion />.
 */
class CurrentVersion extends TTemplateControl
{
}
