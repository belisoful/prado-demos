<?php

class Home extends TPage
{
	public function onLoad($param)
	{
		parent::onLoad($param);
		$this->TemplateSize->Size = filesize(__DIR__ . '/Home.page');
	}
}
