import { ArgsType, Field, InputType } from '@nestjs/graphql';
import { IsDataExisted } from '../IsDataExisted';

@ArgsType()
@InputType()
export class NewDataInput {
	constructor(
		origin: string,
		translated: string,
		translator: string,
		verified: boolean,
	) {
		this.origin = origin;
		this.translated = translated;
		this.translator = translator;
		this.verified = verified;
	}

	private _origin: string;
	@Field()
	get origin(): string {
		return this._origin;
	}
	set origin(value: string) {
		this._origin = value;
	}

	private _translated: string;
	@Field()
	get translated(): string {
		return this._translated;
	}
	set translated(value: string) {
		this._translated = value;
	}

	private _translator: string;
	@Field()
	get translator(): string {
		return this._translator;
	}
	set translator(value: string) {
		this._translator = value;
	}

	@IsDataExisted({ message: 'This data is already existed' })
	get nonHashValue(): string {
		return `${this.origin} ${this.translated} ${this.translator}`;
	}

	@Field()
	verified: boolean;
}
