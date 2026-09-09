<?php

class Home extends TPage
{
	/**
	 * A string render filter. Wraps the control's rendered HTML in a box.
	 */
	public function wrapInBox($sender, $param)
	{
		$html = $param->getFilterText();
		$param->setFilterText(
			'<div style="background:#fffbe6;border:1px solid #e0c060;padding:6px">' . $html . '</div>'
		);
	}

	/**
	 * A DOM render filter. Adds a red outline to every element in the output.
	 */
	public function outlineElements($sender, $param)
	{
		if ($param->getFilterDOM() === false) {
			return;
		}
		$param->walkElements(function ($el, $p) {
			$style = $el->getAttribute('style');
			$el->setAttribute('style', ($style !== '' ? $style . ';' : '') . 'outline:1px solid #c33');
		});
	}
}
